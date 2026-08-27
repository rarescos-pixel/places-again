from __future__ import annotations

import os
from collections import deque
from pathlib import Path
from threading import Lock
from time import monotonic

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from google.adk.runners import InMemoryRunner

from places_again.agent import root_agent
from places_again.models import (
    AgentRequest,
    PlanCommitRequest,
    RecoveryEventRequest,
    RecoveryRequest,
)
from places_again.repository import repository
from places_again.tools import (
    analyze_person_disruption,
    commit_recovery_plan,
    prepare_call_sheets,
    reset_demo,
)


ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Places, Again", version="0.3.0")
_agent_run_times: deque[float] = deque()
_agent_run_lock = Lock()


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
    return {
        "agent_framework": "Google Agent Development Kit",
        "model": os.environ.get("PLACES_AGAIN_MODEL", "gemini-3.5-flash"),
        "model_backend": "Vertex AI" if uses_vertex else "Gemini API",
        "gemini_configured": _gemini_configured(),
        "runtime": "Google Cloud Run" if os.environ.get("K_SERVICE") else "local",
        "repository": os.environ.get("PLACES_AGAIN_REPOSITORY", "json"),
        "agent_runs_per_hour": _agent_runs_per_hour(),
        "cloud_service": os.environ.get("K_SERVICE"),
        "cloud_revision": os.environ.get("K_REVISION"),
    }


@app.get("/api/state")
def get_state() -> dict:
    return repository.snapshot()


@app.get("/api/audit")
def get_audit() -> dict:
    state = repository.snapshot()
    return {"version": state["version"], "audit": state.get("audit", []), "outbox": state.get("outbox", [])}


@app.post("/api/demo/reset")
def reset() -> dict:
    return reset_demo()


@app.post("/api/recover")
def recover(request: RecoveryRequest) -> dict:
    disruption = request.disruption
    plan = analyze_person_disruption(
        disruption.person_id, disruption.start, disruption.end, disruption.reason
    )
    result: dict = {"plan": plan, "committed": False, "call_sheets": []}
    if request.commit and plan["safe_to_commit"]:
        committed = commit_recovery_plan(plan["plan_id"])
        if committed["status"] == "error":
            raise HTTPException(status_code=409, detail=committed["message"])
        english = prepare_call_sheets(plan["plan_id"], "en")
        romanian = prepare_call_sheets(plan["plan_id"], "ro")
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
def run_demo() -> dict:
    reset_demo()
    request = RecoveryRequest(
        disruption={
            "person_id": "soprano_principal",
            "start": "08:00",
            "end": "14:00",
            "reason": "same-day illness",
        },
        commit=True,
    )
    return recover(request)


@app.post("/api/demo/preview")
def preview_demo() -> dict:
    reset_demo()
    request = RecoveryRequest(
        disruption={
            "person_id": "soprano_principal",
            "start": "08:00",
            "end": "14:00",
            "reason": "same-day illness",
        },
        commit=False,
    )
    return recover(request)


@app.post("/api/plans/commit")
def commit_plan(request: PlanCommitRequest) -> dict:
    committed = commit_recovery_plan(request.plan_id)
    if committed["status"] == "error":
        raise HTTPException(status_code=409, detail=committed["message"])
    english = prepare_call_sheets(request.plan_id, "en")
    romanian = prepare_call_sheets(request.plan_id, "ro")
    return {
        "committed": True,
        "new_version": committed["new_version"],
        "state": repository.snapshot(),
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
    runner = InMemoryRunner(agent=root_agent, app_name="places_again")
    events = await runner.run_debug(message, quiet=True)
    messages = []
    trace = []
    for event in events:
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
    return {"messages": messages, "trace": trace, "event_count": len(events)}


@app.post("/api/agent")
async def run_agent(request: AgentRequest) -> dict:
    return await _execute_agent(request.message)


@app.post("/api/events/person-unavailable")
async def receive_person_unavailable_event(request: RecoveryEventRequest) -> dict:
    """Turn an incoming production event into an autonomous recovery workflow."""
    if request.reset_demo:
        reset_demo()
    disruption = request.disruption
    message = (
        "A production-system event reports that "
        f"person_id={disruption.person_id} is unavailable from {disruption.start} "
        f"to {disruption.end}. Reason: {disruption.reason}. Read current state, "
        "analyze every affected call, commit only if all safety gates pass, then "
        "prepare both English and Romanian call sheets. Do not send messages."
    )
    result = await _execute_agent(message)
    return {
        "trigger": "person_unavailable",
        "source": "production_event",
        "disruption": disruption.model_dump(),
        **result,
    }
