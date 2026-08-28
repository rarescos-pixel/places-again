from __future__ import annotations

import os
from collections import deque
from pathlib import Path
from threading import Lock
from time import monotonic, perf_counter

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from fastapi.responses import FileResponse
from google.adk.runners import InMemoryRunner

from places_again.agent import root_agent
from places_again.models import (
    IncidentRequest,
    PlanCommitRequest,
    PubSubEnvelope,
    RecoveryEventRequest,
    RecoveryRequest,
)
from places_again.pubsub import decode_event_id, publish_event
from places_again.repository import repository
from places_again.tools import (
    analyze_person_disruption,
    commit_recovery_plan,
    prepare_call_sheets,
    reset_demo,
)
from places_again.workflow import (
    get_event,
    process_event,
    receive_incident,
    record_agent_observation,
)


ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Places, Again", version="0.7.0")
_agent_run_times: deque[float] = deque()
_agent_run_lock = Lock()


def _env_enabled(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _synthetic_demo_reset_enabled() -> bool:
    """Keep destructive demo reset local unless deployment opts in explicitly."""
    return _env_enabled(
        "PLACES_AGAIN_SYNTHETIC_DEMO_MODE",
        default=not bool(os.environ.get("K_SERVICE")),
    )


def _local_manual_mutation_enabled() -> bool:
    """The public Cloud Run API must not retain legacy direct commit routes."""
    return not bool(os.environ.get("K_SERVICE")) and _env_enabled(
        "PLACES_AGAIN_LOCAL_MANUAL_MODE", default=True
    )


def _require_synthetic_demo_reset() -> None:
    if not _synthetic_demo_reset_enabled():
        raise HTTPException(
            status_code=403,
            detail="Synthetic demo reset is disabled for this deployment.",
        )


def _require_local_manual_mutation() -> None:
    if not _local_manual_mutation_enabled():
        raise HTTPException(
            status_code=403,
            detail="Legacy direct schedule mutation is disabled on Cloud Run.",
        )


def _agent_runs_per_hour() -> int:
    configured = os.environ.get("PLACES_AGAIN_AGENT_RUNS_PER_HOUR", "12")
    try:
        return max(1, int(configured))
    except ValueError:
        return 12


def _claim_agent_run_slot() -> None:
    """Bound public Gemini usage for the single-instance contest demo."""
    cutoff = monotonic() - 3600
    with _agent_run_lock:
        while _agent_run_times and _agent_run_times[0] < cutoff:
            _agent_run_times.popleft()
        if len(_agent_run_times) >= _agent_runs_per_hour():
            raise HTTPException(
                status_code=429,
                detail=(
                    "The public Gemini demo reached its hourly safety limit. "
                    "The deterministic preview remains available; try the "
                    "Gemini workflow again later."
                ),
            )
        _agent_run_times.append(monotonic())


def _gemini_configured() -> bool:
    has_api_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    uses_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    has_vertex_project = bool(os.environ.get("GOOGLE_CLOUD_PROJECT"))
    return has_api_key or (uses_vertex and has_vertex_project)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "places-again"}


@app.get("/api/capabilities")
def capabilities() -> dict:
    uses_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    uses_pubsub_worker = bool(os.environ.get("PLACES_AGAIN_PUBSUB_TOPIC"))
    service_role = os.environ.get("PLACES_AGAIN_SERVICE_ROLE", "all-in-one-local")
    repository_mode = os.environ.get("PLACES_AGAIN_REPOSITORY", "json").lower()
    return {
        "agent_framework": "Google Agent Development Kit",
        "model": os.environ.get("PLACES_AGAIN_MODEL", "gemini-3.5-flash"),
        "model_backend": "Vertex AI" if uses_vertex or uses_pubsub_worker else "Gemini API",
        "gemini_configured": _gemini_configured() or uses_pubsub_worker,
        "runtime": "Google Cloud Run" if os.environ.get("K_SERVICE") else "local",
        "repository": repository_mode,
        "event_transport": (
            "Google Pub/Sub"
            if os.environ.get("PLACES_AGAIN_PUBSUB_TOPIC")
            else "local background worker"
        ),
        "service_role": service_role,
        "private_worker_configured": uses_pubsub_worker,
        "effect_semantics": (
            "exactly-once business effect via Firestore transaction"
            if repository_mode == "firestore"
            else "single-process idempotent fallback; cloud proof required"
        ),
        "scenarios": ["opera", "commercial_shoot"],
        "autonomy_policy": "safe auto-commit; unresolved human escalation",
        "gemini_role": "structured selection among deterministic safe candidates",
        "hard_safety_owner": "deterministic constraint engine and atomic transaction",
        "candidate_limit": 5,
        "outbound_delivery": "disabled; prepared_not_sent only",
        "synthetic_demo_reset_enabled": _synthetic_demo_reset_enabled(),
        "legacy_direct_mutation_enabled": _local_manual_mutation_enabled(),
        "agent_runs_per_hour": _agent_runs_per_hour(),
        "cloud_service": os.environ.get("K_SERVICE"),
        "cloud_revision": os.environ.get("K_REVISION"),
    }


@app.get("/api/state")
def get_state(
    scenario_id: str = Query(default="opera", pattern=r"^[a-z][a-z0-9_-]{1,63}$")
) -> dict:
    try:
        return repository.snapshot(scenario_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/audit")
def get_audit(
    scenario_id: str = Query(default="opera", pattern=r"^[a-z][a-z0-9_-]{1,63}$")
) -> dict:
    try:
        state = repository.snapshot(scenario_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"version": state["version"], "audit": state.get("audit", []), "outbox": state.get("outbox", [])}


@app.post("/api/demo/reset")
def reset(scenario_id: str = "opera") -> dict:
    _require_synthetic_demo_reset()
    try:
        return reset_demo(scenario_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/recover")
def recover(request: RecoveryRequest) -> dict:
    if request.commit:
        _require_local_manual_mutation()
    disruption = request.disruption
    plan = analyze_person_disruption(
        disruption.person_id,
        disruption.start,
        disruption.end,
        disruption.reason,
        request.scenario_id,
    )
    result: dict = {"plan": plan, "committed": False, "call_sheets": []}
    if request.commit and plan["safe_to_commit"]:
        committed = commit_recovery_plan(plan["plan_id"], request.scenario_id)
        if committed["status"] == "error":
            raise HTTPException(status_code=409, detail=committed["message"])
        english = prepare_call_sheets(plan["plan_id"], "en", request.scenario_id)
        romanian = prepare_call_sheets(plan["plan_id"], "ro", request.scenario_id)
        result.update(
            {
                "committed": True,
                "new_version": committed["new_version"],
                "state": committed["state"],
                "call_sheets": english["messages"] + romanian["messages"],
            }
        )
    return result


@app.post("/api/demo/run")
def run_demo(scenario_id: str = "opera") -> dict:
    _require_synthetic_demo_reset()
    _require_local_manual_mutation()
    reset_demo(scenario_id)
    if scenario_id == "commercial_shoot":
        person_id, start, end = "dp_principal", "07:00", "16:00"
    else:
        person_id, start, end = "soprano_principal", "08:00", "14:00"
    request = RecoveryRequest(
        scenario_id=scenario_id,
        disruption={
            "person_id": person_id,
            "start": start,
            "end": end,
            "reason": "same-day illness",
        },
        commit=True,
    )
    return recover(request)


@app.post("/api/demo/preview")
def preview_demo(scenario_id: str = "opera") -> dict:
    _require_synthetic_demo_reset()
    _require_local_manual_mutation()
    reset_demo(scenario_id)
    if scenario_id == "commercial_shoot":
        person_id, start, end = "dp_principal", "07:00", "16:00"
    else:
        person_id, start, end = "soprano_principal", "08:00", "14:00"
    request = RecoveryRequest(
        scenario_id=scenario_id,
        disruption={
            "person_id": person_id,
            "start": start,
            "end": end,
            "reason": "same-day illness",
        },
        commit=False,
    )
    return recover(request)


@app.post("/api/plans/commit")
def commit_plan(request: PlanCommitRequest) -> dict:
    _require_local_manual_mutation()
    committed = commit_recovery_plan(request.plan_id, request.scenario_id)
    if committed["status"] == "error":
        raise HTTPException(status_code=409, detail=committed["message"])
    english = prepare_call_sheets(request.plan_id, "en", request.scenario_id)
    romanian = prepare_call_sheets(request.plan_id, "ro", request.scenario_id)
    return {
        "committed": True,
        "new_version": committed["new_version"],
        "state": repository.snapshot(request.scenario_id),
        "call_sheets": english["messages"] + romanian["messages"],
    }


async def _execute_agent(message: str) -> dict:
    if not _gemini_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Configure a Gemini API key or Vertex AI Application Default "
                "Credentials to run the Google ADK path."
            ),
        )
    _claim_agent_run_slot()
    started = perf_counter()
    runner = InMemoryRunner(agent=root_agent, app_name="places_again")
    events = await runner.run_debug(message, quiet=True)
    messages = []
    trace = []
    usage = {"prompt_tokens": 0, "candidate_tokens": 0, "total_tokens": 0}
    for event in events:
        metadata = getattr(event, "usage_metadata", None)
        if metadata:
            usage["prompt_tokens"] += int(
                getattr(metadata, "prompt_token_count", 0) or 0
            )
            usage["candidate_tokens"] += int(
                getattr(metadata, "candidates_token_count", 0) or 0
            )
            usage["total_tokens"] += int(
                getattr(metadata, "total_token_count", 0) or 0
            )
        content = getattr(event, "content", None)
        if not content:
            continue
        text_parts = []
        for part in content.parts or []:
            if getattr(part, "text", None):
                text_parts.append(part.text)
            function_call = getattr(part, "function_call", None)
            if function_call:
                trace.append(
                    {
                        "type": "tool_call",
                        "name": function_call.name,
                        "arguments": dict(function_call.args or {}),
                    }
                )
            function_response = getattr(part, "function_response", None)
            if function_response:
                trace.append(
                    {
                        "type": "tool_result",
                        "name": function_response.name,
                        "result": function_response.response,
                    }
                )
        text = "".join(text_parts)
        if text:
            messages.append(text)
    return {
        "messages": messages,
        "trace": trace,
        "event_count": len(events),
        "latency_ms": round((perf_counter() - started) * 1000, 2),
        "usage": usage,
    }


async def _execute_event_agent(event_id: str) -> dict:
    result = await _execute_agent(
        "Process trusted event_id="
        f"{event_id}. Follow the fixed event workflow and use only the allowed tools."
    )
    record_agent_observation(
        event_id,
        trace=result["trace"],
        event_count=result["event_count"],
        model=os.environ.get("PLACES_AGAIN_MODEL", "gemini-3.5-flash"),
        latency_ms=result["latency_ms"],
        usage=result["usage"],
        repository=repository,
    )
    return result


def _record_ignored_pubsub_push(reason: str, message_id: str | None) -> None:
    """Leave a compact audit record while acknowledging poison deliveries."""
    def record(system: dict) -> tuple[dict, None]:
        system.setdefault("audit", []).append(
            {
                "event": "pubsub_push_ignored",
                "reason": reason,
                "message_id": message_id,
            }
        )
        return system, None

    try:
        repository.mutate_system(record)
    except Exception:
        # A poison payload must not turn a transient audit-write problem into an
        # unbounded Pub/Sub retry. Cloud logging still captures the request.
        return


@app.post("/api/events", status_code=status.HTTP_202_ACCEPTED)
def create_event(request: IncidentRequest, background_tasks: BackgroundTasks) -> dict:
    """Accept quickly, persist first, then publish an opaque id for background work."""
    try:
        event = receive_incident(
            request.scenario_id,
            request.disruption.model_dump(),
            event_id=request.event_id,
            source=request.source,
            repository=repository,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    try:
        publication = publish_event(event["event_id"])
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail={
                "event_id": event["event_id"],
                "status": event["status"],
                "retryable": True,
                "message": "incident persisted but Pub/Sub publish failed; retry this event_id",
                "error_type": type(error).__name__,
            },
        ) from error
    if publication["mode"] == "local_background":
        background_tasks.add_task(
            process_event,
            event["event_id"],
            repository=repository,
            orchestration="local_background_worker",
        )
    return {
        "event_id": event["event_id"],
        "status": event["status"],
        "duplicate_delivery": event.get("duplicate_delivery", False),
        "transport": publication["mode"],
        "status_url": f"/api/events/{event['event_id']}",
    }


@app.get("/api/events/{event_id}")
def event_status(event_id: str) -> dict:
    event = get_event(event_id, repository=repository)
    if event is None:
        raise HTTPException(status_code=404, detail="unknown event_id")
    return event


@app.post("/api/pubsub/push")
async def pubsub_push(envelope: PubSubEnvelope) -> dict:
    """Private Cloud Run worker target; Cloud Run IAM verifies Pub/Sub OIDC."""
    if os.environ.get("PLACES_AGAIN_SERVICE_ROLE") != "worker":
        # Both Cloud Run services use the same immutable image. Keep the worker
        # entrypoint unreachable on the public API deployment as defense in
        # depth behind the private service's ingress and IAM controls.
        raise HTTPException(status_code=404, detail="worker endpoint unavailable")
    try:
        event_id = decode_event_id(envelope.message.data)
    except ValueError:
        _record_ignored_pubsub_push("invalid_payload", envelope.message.message_id)
        return {"status": "ignored", "reason": "invalid_payload"}
    event = get_event(event_id, repository=repository)
    if event is None:
        _record_ignored_pubsub_push("unknown_event_id", envelope.message.message_id)
        return {"event_id": event_id, "status": "ignored", "reason": "unknown_event_id"}
    if event["status"] in {"completed", "human_required"}:
        replay = process_event(
            event_id,
            repository=repository,
            orchestration="pubsub_replay",
        )
        return {"event_id": event_id, "status": replay["status"], "replay": True}
    agent_result = await _execute_event_agent(event_id)
    final = get_event(event_id, repository=repository)
    if final is None or final["status"] not in {"completed", "human_required"}:
        raise HTTPException(
            status_code=500,
            detail="ADK run ended without a terminal workflow state; Pub/Sub should retry",
        )
    return {
        "event_id": event_id,
        "status": final["status"],
        "agent_events": agent_result["event_count"],
    }


@app.post(
    "/api/events/person-unavailable",
    status_code=status.HTTP_202_ACCEPTED,
    deprecated=True,
)
def receive_person_unavailable_event(
    request: RecoveryEventRequest, background_tasks: BackgroundTasks
) -> dict:
    """Compatibility alias for the generic event endpoint."""
    if request.reset_demo:
        _require_synthetic_demo_reset()
        reset_demo(request.scenario_id)
    incident = IncidentRequest(
        scenario_id=request.scenario_id,
        disruption=request.disruption,
        source="demo",
    )
    return create_event(incident, background_tasks)
