from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

from places_again.engine import apply_plan, build_recovery_plan, create_call_sheets
from places_again.observability import emit
from places_again.repository import repository as default_repository


TERMINAL_STATUSES = {"completed", "human_required"}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _transition(event: dict[str, Any], status: str, at: str) -> None:
    event["status"] = status
    event.setdefault("status_history", []).append({"status": status, "at": at})


def receive_incident(
    scenario_id: str,
    disruption: dict[str, Any],
    *,
    event_id: UUID | str | None = None,
    source: str = "api",
    repository=default_repository,
) -> dict[str, Any]:
    """Persist an incident before publishing it to the background worker."""
    stable_event_id = str(event_id or uuid4())
    received_at = _timestamp()

    def receive(system: dict[str, Any]):
        if scenario_id not in system["scenarios"]:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        existing = system.setdefault("events", {}).get(stable_event_id)
        if existing:
            if (
                existing["scenario_id"] != scenario_id
                or existing["disruption"] != disruption
            ):
                raise ValueError("event_id is already bound to a different incident")
            result = deepcopy(existing)
            result["duplicate_delivery"] = True
            return system, result

        scenario = system["scenarios"][scenario_id]
        event = {
            "event_id": stable_event_id,
            "correlation_id": stable_event_id,
            "scenario_id": scenario_id,
            "source": source,
            "status": "received",
            "status_history": [{"status": "received", "at": received_at}],
            "created_at": received_at,
            "updated_at": received_at,
            "received_version": scenario["version"],
            "disruption": deepcopy(disruption),
            "attempts": 0,
            "retry_count": 0,
            "duplicate_deliveries": 0,
            "messages_sent": 0,
        }
        system["events"][stable_event_id] = event
        system.setdefault("audit", []).append(
            {
                "event": "incident_received",
                "event_id": stable_event_id,
                "scenario_id": scenario_id,
                "at": received_at,
            }
        )
        return system, deepcopy(event)

    result = repository.mutate_system(receive)
    emit(
        "incident_received",
        event_id=stable_event_id,
        correlation_id=stable_event_id,
        scenario_id=scenario_id,
        duplicate=result.get("duplicate_delivery", False),
    )
    return result


def get_event(event_id: str, *, repository=default_repository) -> dict[str, Any] | None:
    return deepcopy(repository.system_snapshot().get("events", {}).get(event_id))


def record_agent_observation(
    event_id: str,
    *,
    trace: list[dict[str, Any]],
    event_count: int,
    model: str,
    latency_ms: float | None = None,
    usage: dict[str, int] | None = None,
    repository=default_repository,
) -> dict[str, Any]:
    """Persist observable ADK actions without storing hidden model reasoning."""
    recorded_at = _timestamp()

    def record(system: dict[str, Any]):
        event = system.get("events", {}).get(event_id)
        if event is None:
            raise ValueError(f"Unknown event: {event_id}")
        event["model"] = model
        event["agent_event_count"] = event_count
        event["agent_trace"] = deepcopy(trace)
        event["agent_latency_ms"] = latency_ms
        event["model_usage"] = deepcopy(usage or {})
        event["agent_trace_recorded_at"] = recorded_at
        event["updated_at"] = recorded_at
        return system, deepcopy(event)

    result = repository.mutate_system(record)
    emit(
        "agent_observation_recorded",
        event_id=event_id,
        correlation_id=event_id,
        model=model,
        latency_ms=latency_ms,
        tool_events=len(trace),
        usage=usage or {},
    )
    return result


def process_event(
    event_id: str,
    *,
    repository=default_repository,
    orchestration: str = "deterministic_worker",
    model: str | None = None,
    crash_at: str | None = None,
) -> dict[str, Any]:
    """Execute exactly-once recovery effects inside one atomic transaction.

    Pub/Sub is at-least-once. The event ledger, schedule version, committed plan,
    audit trail, and outbox are changed together, so retries can only return the
    already-recorded terminal result. `crash_at` is test-only fault injection.
    """
    started = perf_counter()
    attempt_at = _timestamp()

    def execute(system: dict[str, Any]):
        event = system.setdefault("events", {}).get(event_id)
        if event is None:
            raise ValueError(f"Unknown event: {event_id}")
        if event["status"] in TERMINAL_STATUSES:
            event["duplicate_deliveries"] = event.get("duplicate_deliveries", 0) + 1
            event["updated_at"] = attempt_at
            result = deepcopy(event)
            result["duplicate_delivery"] = True
            return system, result

        event["attempts"] = event.get("attempts", 0) + 1
        event["retry_count"] = max(0, event["attempts"] - 1)
        event["orchestration"] = orchestration
        event["model"] = model
        _transition(event, "analyzing", attempt_at)
        scenario_id = event["scenario_id"]
        state = deepcopy(system["scenarios"][scenario_id])
        event["base_version"] = state["version"]
        plan_id = f"plan-{event_id.replace('-', '')[:16]}"

        try:
            plan = build_recovery_plan(
                state, event["disruption"], plan_id=plan_id
            )
        except ValueError as error:
            event["failure"] = {
                "type": "invalid_or_unknown_incident",
                "message": str(error),
            }
            _transition(event, "human_required", attempt_at)
            event["human_reason"] = (
                "Human decision required — the incident cannot be safely "
                "resolved under the current policy."
            )
            event["updated_at"] = attempt_at
            event["processing_elapsed_ms"] = round(
                (perf_counter() - started) * 1000, 2
            )
            return system, deepcopy(event)

        event["plan_id"] = plan["plan_id"]
        event["plan"] = deepcopy(plan)
        event["metrics"] = deepcopy(plan["metrics"])
        _transition(event, "planned", attempt_at)
        if crash_at == "after_plan":
            raise RuntimeError("fault injection: crash after plan")
        _transition(event, "verified", attempt_at)
        event["verification"] = deepcopy(plan["verification"])

        if not plan["affected_activities"]:
            event["outcome"] = "no_affected_activities"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_required"
            _transition(event, "completed", attempt_at)
            event["updated_at"] = attempt_at
            event["processing_elapsed_ms"] = round(
                (perf_counter() - started) * 1000, 2
            )
            return system, deepcopy(event)

        if not plan["safe_to_commit"]:
            event["outcome"] = "human_escalation"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_prepared"
            event["human_reason"] = (
                "Human decision required — no safe recovery exists under "
                "current policy."
            )
            _transition(event, "human_required", attempt_at)
            event["updated_at"] = attempt_at
            event["processing_elapsed_ms"] = round(
                (perf_counter() - started) * 1000, 2
            )
            system.setdefault("audit", []).append(
                {
                    "event": "incident_escalated",
                    "event_id": event_id,
                    "scenario_id": scenario_id,
                    "at": attempt_at,
                    "unresolved": plan["metrics"]["unresolved_activities"],
                }
            )
            return system, deepcopy(event)

        if crash_at == "before_commit":
            raise RuntimeError("fault injection: crash before commit")
        updated = apply_plan(state, plan)
        updated.setdefault("recovery_plans", {})[plan_id] = {
            "status": "committed",
            "event_id": event_id,
            "committed_version": updated["version"],
            "plan": deepcopy(plan),
        }
        _transition(event, "committed", attempt_at)
        event["final_version"] = updated["version"]

        messages = create_call_sheets(updated, plan, "en") + create_call_sheets(
            updated, plan, "ro"
        )
        existing_ids = {message["id"] for message in updated.get("outbox", [])}
        new_messages = []
        for message in messages:
            message["event_id"] = event_id
            if message["id"] not in existing_ids:
                new_messages.append(message)
        updated.setdefault("outbox", []).extend(new_messages)
        updated.setdefault("audit", []).append(
            {
                "event": "event_outbox_prepared",
                "event_id": event_id,
                "plan_id": plan_id,
                "count": len(new_messages),
                "delivery_status": "prepared_not_sent",
            }
        )
        system["scenarios"][scenario_id] = updated
        _transition(event, "outbox_prepared", attempt_at)
        event["outbox_status"] = "prepared_not_sent"
        event["outbox_count"] = len(messages)
        event["messages_sent"] = 0
        event["outcome"] = "autonomous_safe_commit"
        if crash_at == "after_commit_before_completion":
            raise RuntimeError("fault injection: crash after provisional commit")
        _transition(event, "completed", attempt_at)
        event["updated_at"] = attempt_at
        event["processing_elapsed_ms"] = round(
            (perf_counter() - started) * 1000, 2
        )
        event["action_trace"] = [
            {
                "type": "deterministic_recovery_action",
                "activity_id": action["activity_id"],
                "action": action["type"],
            }
            for action in plan["actions"]
        ]
        system.setdefault("audit", []).append(
            {
                "event": "incident_completed",
                "event_id": event_id,
                "scenario_id": scenario_id,
                "plan_id": plan_id,
                "base_version": plan["base_version"],
                "final_version": updated["version"],
                "verification_passed": plan["verification"]["passed"],
                "outbox_status": "prepared_not_sent",
                "messages_sent": 0,
                "at": attempt_at,
            }
        )
        return system, deepcopy(event)

    result = repository.mutate_system(execute)
    emit(
        "incident_processing_finished",
        event_id=event_id,
        correlation_id=event_id,
        scenario_id=result.get("scenario_id"),
        status=result.get("status"),
        outcome=result.get("outcome"),
        base_version=result.get("base_version"),
        final_version=result.get("final_version"),
        retry_count=result.get("retry_count"),
        messages_sent=result.get("messages_sent", 0),
    )
    return result
