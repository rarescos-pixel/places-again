from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

from places_again.engine import (
    apply_plan,
    build_recovery_candidates,
    create_call_sheets,
    reverify_recovery_plan,
)
from places_again.observability import emit
from places_again.repository import repository as default_repository


TERMINAL_STATUSES = {"completed", "human_required"}
SELECTION_REASON_METRICS = {
    "preserve_highest_priority_activity": (
        "highest_priority_activities_moved",
        "preserves the highest-priority activity",
    ),
    "minimize_people_schedule_changes": (
        "people_schedule_changed",
        "changes fewer people's schedules",
    ),
    "minimize_shifted_minutes": (
        "shifted_minutes",
        "minimizes total shifted minutes",
    ),
    "minimize_resource_rescheduling": (
        "resources_rescheduled",
        "reschedules fewer scarce resources",
    ),
    "balance_cover_workload": (
        "maximum_cover_minutes",
        "balances work across qualified covers",
    ),
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _transition(event: dict[str, Any], status: str, at: str) -> None:
    event["status"] = status
    event.setdefault("status_history", []).append({"status": status, "at": at})


def _candidate_view(
    state: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    activity_by_id = {
        activity["id"]: activity
        for activity in state.get("activities", state.get("sessions", []))
    }
    return {
        "candidate_id": candidate["candidate_id"],
        "plan_id": candidate["plan_id"],
        "hard_constraints": "PASS",
        "metrics": deepcopy(candidate["selection_evidence"]),
        "actions": [
            {
                "activity_id": action["activity_id"],
                "activity": activity_by_id.get(action["activity_id"], {}).get(
                    "title", action["activity_id"]
                ),
                "priority": activity_by_id.get(action["activity_id"], {}).get(
                    "priority", 0
                ),
                "cover": state["people"].get(action["new_person_id"], {}).get(
                    "name", action["new_person_id"]
                ),
                "old_start": action["old_start"],
                "new_start": action["new_start"],
            }
            for action in candidate["actions"]
        ],
    }


def _validated_selection_reasons(
    selected: dict[str, Any],
    candidates: list[dict[str, Any]],
    requested_codes: list[str] | None,
    allowed_codes: set[str],
) -> tuple[list[str], list[str], list[str]]:
    requested = requested_codes if isinstance(requested_codes, list) else []
    valid: list[str] = []
    invalid: list[str] = []
    labels: list[str] = []
    if not 1 <= len(requested) <= 2:
        invalid.append("reason_codes_must_contain_one_or_two_values")
    if not all(isinstance(code, str) for code in requested):
        invalid.append("reason_code_must_be_a_string")
    elif len(requested) != len(set(requested)):
        invalid.append("reason_codes_must_be_unique")
    for code in requested:
        if not isinstance(code, str):
            continue
        if code not in allowed_codes:
            invalid.append(f"reason_code_not_in_event_policy:{code}")
            continue
        rule = SELECTION_REASON_METRICS.get(code)
        if rule is None:
            invalid.append(f"reason_code_not_observable:{code}")
            continue
        metric, label = rule
        if metric not in selected.get("selection_evidence", {}):
            invalid.append(f"reason_metric_not_exposed:{code}")
            continue
        if selected["selection_evidence"][metric] != selected["metrics"].get(metric):
            invalid.append(f"reason_metric_evidence_mismatch:{code}")
            continue
        best_value = min(candidate["metrics"][metric] for candidate in candidates)
        if selected["metrics"][metric] != best_value:
            invalid.append(f"reason_not_supported_by_selected_candidate:{code}")
            continue
        valid.append(code)
        labels.append(label)
    if invalid:
        return [], [], invalid
    return valid, labels, []


def _deterministic_selection_reasons(
    selected: dict[str, Any], candidates: list[dict[str, Any]], allowed_codes: set[str]
) -> list[str]:
    supported = []
    for code, (metric, _) in SELECTION_REASON_METRICS.items():
        if code not in allowed_codes:
            continue
        best_value = min(candidate["metrics"][metric] for candidate in candidates)
        if selected["metrics"][metric] == best_value:
            supported.append(code)
        if len(supported) == 2:
            break
    return supported


def _event_soft_priority_codes(event: dict[str, Any]) -> set[str]:
    """Return only the reason codes explicitly persisted with this event."""
    return {
        priority["code"]
        for priority in event.get("soft_priorities", [])
        if isinstance(priority, dict) and isinstance(priority.get("code"), str)
    }


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


def prepare_event_candidates(
    event_id: str,
    *,
    repository=default_repository,
    orchestration: str = "google_adk_gemini",
    model: str | None = None,
) -> dict[str, Any]:
    """Persist a bounded safe choice set without changing the schedule."""
    prepared_at = _timestamp()

    def prepare(system: dict[str, Any]):
        event = system.setdefault("events", {}).get(event_id)
        if event is None:
            raise ValueError(f"Unknown event: {event_id}")
        if event["status"] in TERMINAL_STATUSES:
            result = deepcopy(event)
            result["duplicate_delivery"] = True
            return system, result
        if event.get("candidate_set"):
            result = deepcopy(event)
            result["candidate_preparation_replayed"] = True
            return system, result

        event["attempts"] = event.get("attempts", 0) + 1
        event["retry_count"] = max(0, event["attempts"] - 1)
        event["orchestration"] = orchestration
        event["model"] = model
        _transition(event, "analyzing", prepared_at)
        scenario_id = event["scenario_id"]
        state = deepcopy(system["scenarios"][scenario_id])
        event["base_version"] = state["version"]
        base_plan_id = f"plan-{event_id.replace('-', '')[:16]}"
        try:
            candidate_set = build_recovery_candidates(
                state, event["disruption"], plan_id=base_plan_id
            )
        except ValueError as error:
            event["failure"] = {
                "type": "invalid_or_unknown_incident",
                "message": str(error),
            }
            event["human_reason"] = (
                "Human decision required — the incident cannot be safely "
                "resolved under the current policy."
            )
            _transition(event, "human_required", prepared_at)
            event["updated_at"] = prepared_at
            return system, deepcopy(event)

        candidates = candidate_set["candidates"]
        event["candidate_set"] = deepcopy(candidate_set)
        event["candidate_set_id"] = candidate_set["candidate_set_id"]
        event["safe_candidates_considered"] = len(candidates)
        event["candidate_summaries"] = [
            _candidate_view(state, candidate) for candidate in candidates
        ]
        event["soft_priorities"] = deepcopy(candidate_set["soft_priorities"])
        representative = candidates[0] if candidates else candidate_set["fallback_plan"]
        event["metrics"] = deepcopy(representative["metrics"])
        _transition(event, "planned", prepared_at)
        event["updated_at"] = prepared_at
        system.setdefault("audit", []).append(
            {
                "event": "safe_candidates_generated",
                "event_id": event_id,
                "scenario_id": scenario_id,
                "candidate_set_id": candidate_set["candidate_set_id"],
                "safe_candidates": len(candidates),
                "base_version": state["version"],
                "at": prepared_at,
            }
        )

        if not candidates:
            event["plan"] = deepcopy(candidate_set["fallback_plan"])
            event["verification"] = deepcopy(
                candidate_set["fallback_plan"]["verification"]
            )
            event["outcome"] = "human_escalation"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_prepared"
            event["human_reason"] = (
                "Human decision required — no safe recovery exists under "
                "current policy."
            )
            _transition(event, "human_required", prepared_at)
        return system, deepcopy(event)

    result = repository.mutate_system(prepare)
    emit(
        "safe_candidates_prepared",
        event_id=event_id,
        correlation_id=event_id,
        status=result.get("status"),
        candidate_set_id=result.get("candidate_set_id"),
        safe_candidates=result.get("safe_candidates_considered", 0),
        base_version=result.get("base_version"),
    )
    return result


def commit_event_candidate(
    event_id: str,
    candidate_id: str,
    reason_codes: list[str] | None = None,
    *,
    repository=default_repository,
    selector: str = "gemini_structured_selection",
) -> dict[str, Any]:
    """Validate one candidate ID, re-prove it, then atomically commit effects."""
    selected_at = _timestamp()
    started = perf_counter()

    def select_and_commit(system: dict[str, Any]):
        event = system.setdefault("events", {}).get(event_id)
        if event is None:
            raise ValueError(f"Unknown event: {event_id}")
        if event["status"] in TERMINAL_STATUSES:
            event["duplicate_deliveries"] = event.get("duplicate_deliveries", 0) + 1
            event["updated_at"] = selected_at
            result = deepcopy(event)
            result["duplicate_delivery"] = True
            return system, result

        candidate_set = event.get("candidate_set")
        if not candidate_set:
            event["failure"] = {
                "type": "candidate_set_missing",
                "message": "Safe candidates must be prepared before selection.",
            }
            event["human_reason"] = (
                "Human decision required — no verified candidate set was available."
            )
            _transition(event, "human_required", selected_at)
            event["updated_at"] = selected_at
            return system, deepcopy(event)

        candidates = candidate_set["candidates"]
        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate["candidate_id"] == candidate_id
            ),
            None,
        )
        if selected is None:
            event["failure"] = {
                "type": "invalid_candidate_selection",
                "message": "The selected candidate_id was not in the deterministic safe set.",
                "candidate_id": candidate_id,
            }
            event["human_reason"] = (
                "Human decision required — Gemini returned a candidate outside "
                "the deterministic safe set."
            )
            event["selector"] = selector
            _transition(event, "human_required", selected_at)
            event["updated_at"] = selected_at
            return system, deepcopy(event)

        scenario_id = event["scenario_id"]
        state = deepcopy(system["scenarios"][scenario_id])
        allowed_reason_codes = _event_soft_priority_codes(event)
        valid_codes, labels, unsupported = _validated_selection_reasons(
            selected, candidates, reason_codes, allowed_reason_codes
        )
        event["selector"] = selector
        event["requested_selection_reason_codes"] = deepcopy(reason_codes)
        if unsupported:
            event["failure"] = {
                "type": "invalid_selection_reason_codes",
                "message": "Selection reasons must be one or two unique event-policy codes supported by the selected candidate.",
                "violations": unsupported,
            }
            event["outcome"] = "human_escalation"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_prepared"
            event["human_reason"] = (
                "Human decision required — Gemini supplied invalid or unsupported "
                "selection reasons."
            )
            _transition(event, "human_required", selected_at)
            event["updated_at"] = selected_at
            return system, deepcopy(event)
        event["selected_candidate_id"] = candidate_id
        event["selected_plan_id"] = selected["plan_id"]
        event["selection_reason_codes"] = valid_codes
        event["selection_rationale"] = labels
        event["unsupported_reason_codes"] = unsupported
        event["plan_id"] = selected["plan_id"]
        event["plan"] = deepcopy(selected)
        event["metrics"] = deepcopy(selected["metrics"])
        _transition(event, "candidate_selected", selected_at)

        reverified = reverify_recovery_plan(state, selected)
        event["deterministic_reverification"] = deepcopy(reverified)
        event["verification"] = deepcopy(reverified)
        _transition(event, "verified", selected_at)
        if not reverified["passed"]:
            event["failure"] = {
                "type": "deterministic_reverification_failed",
                "message": "Selected candidate failed current-state hard constraints.",
            }
            event["outcome"] = "human_escalation"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_prepared"
            event["human_reason"] = (
                "Human decision required — the selected candidate failed "
                "deterministic re-verification."
            )
            _transition(event, "human_required", selected_at)
            event["updated_at"] = selected_at
            return system, deepcopy(event)

        if not selected["affected_activities"]:
            event["outcome"] = "no_affected_activities"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_required"
            _transition(event, "completed", selected_at)
            event["updated_at"] = selected_at
            event["processing_elapsed_ms"] = round(
                (perf_counter() - started) * 1000, 2
            )
            return system, deepcopy(event)

        try:
            updated = apply_plan(state, selected)
        except ValueError as error:
            event["failure"] = {
                "type": "deterministic_commit_rejected",
                "message": str(error),
            }
            event["outcome"] = "human_escalation"
            event["final_version"] = state["version"]
            event["outbox_status"] = "not_prepared"
            event["human_reason"] = (
                "Human decision required — the atomic safety gate rejected "
                "the selected candidate."
            )
            _transition(event, "human_required", selected_at)
            event["updated_at"] = selected_at
            return system, deepcopy(event)

        updated.setdefault("recovery_plans", {})[selected["plan_id"]] = {
            "status": "committed",
            "event_id": event_id,
            "committed_version": updated["version"],
            "candidate_id": candidate_id,
            "selector": selector,
            "plan": deepcopy(selected),
        }
        _transition(event, "committed", selected_at)
        event["final_version"] = updated["version"]
        messages = create_call_sheets(updated, selected, "en") + create_call_sheets(
            updated, selected, "ro"
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
                "plan_id": selected["plan_id"],
                "candidate_id": candidate_id,
                "count": len(new_messages),
                "delivery_status": "prepared_not_sent",
            }
        )
        system["scenarios"][scenario_id] = updated
        _transition(event, "outbox_prepared", selected_at)
        event["outbox_status"] = "prepared_not_sent"
        event["outbox_count"] = len(messages)
        event["messages_sent"] = 0
        event["outcome"] = "autonomous_safe_commit"
        _transition(event, "completed", selected_at)
        event["updated_at"] = selected_at
        event["processing_elapsed_ms"] = round(
            (perf_counter() - started) * 1000, 2
        )
        event["action_trace"] = [
            {
                "type": "deterministic_recovery_action",
                "activity_id": action["activity_id"],
                "action": action["type"],
            }
            for action in selected["actions"]
        ]
        system.setdefault("audit", []).append(
            {
                "event": "incident_completed",
                "event_id": event_id,
                "scenario_id": scenario_id,
                "plan_id": selected["plan_id"],
                "candidate_id": candidate_id,
                "selector": selector,
                "selection_reason_codes": valid_codes,
                "base_version": selected["base_version"],
                "final_version": updated["version"],
                "verification_passed": reverified["passed"],
                "outbox_status": "prepared_not_sent",
                "messages_sent": 0,
                "at": selected_at,
            }
        )
        return system, deepcopy(event)

    result = repository.mutate_system(select_and_commit)
    emit(
        "candidate_selection_finished",
        event_id=event_id,
        correlation_id=event_id,
        selector=result.get("selector"),
        selected_candidate_id=result.get("selected_candidate_id"),
        status=result.get("status"),
        reverified=result.get("deterministic_reverification", {}).get("passed"),
        base_version=result.get("base_version"),
        final_version=result.get("final_version"),
        messages_sent=result.get("messages_sent", 0),
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
    """Execute idempotent recovery effects inside one repository transaction.

    In the Firestore cloud deployment, the event ledger, schedule version,
    committed plan, audit, and outbox change in one cross-instance transaction,
    so Pub/Sub retries have exactly-once business effects. The JSON repository
    provides a single-process fallback. `crash_at` is test-only fault injection.
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
        base_plan_id = f"plan-{event_id.replace('-', '')[:16]}"

        try:
            candidate_set = build_recovery_candidates(
                state, event["disruption"], plan_id=base_plan_id
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

        candidates = candidate_set["candidates"]
        event["candidate_set"] = deepcopy(candidate_set)
        event["candidate_set_id"] = candidate_set["candidate_set_id"]
        event["safe_candidates_considered"] = len(candidates)
        event["candidate_summaries"] = [
            _candidate_view(state, candidate) for candidate in candidates
        ]
        event["soft_priorities"] = deepcopy(candidate_set["soft_priorities"])
        plan = candidates[0] if candidates else candidate_set["fallback_plan"]
        plan_id = plan["plan_id"]
        event["plan_id"] = plan["plan_id"]
        event["plan"] = deepcopy(plan)
        event["metrics"] = deepcopy(plan["metrics"])
        _transition(event, "planned", attempt_at)
        if crash_at == "after_plan":
            raise RuntimeError("fault injection: crash after plan")
        if candidates:
            allowed_reason_codes = _event_soft_priority_codes(event)
            reason_codes = _deterministic_selection_reasons(
                plan, candidates, allowed_reason_codes
            )
            valid_codes, labels, invalid_reasons = _validated_selection_reasons(
                plan, candidates, reason_codes, allowed_reason_codes
            )
            if invalid_reasons:
                raise RuntimeError(
                    "deterministic fallback could not produce valid selection reasons"
                )
            event["selector"] = "bounded_deterministic_fallback"
            event["selected_candidate_id"] = plan["candidate_id"]
            event["selected_plan_id"] = plan["plan_id"]
            event["selection_reason_codes"] = valid_codes
            event["selection_rationale"] = labels
            _transition(event, "candidate_selected", attempt_at)
            reverified = reverify_recovery_plan(state, plan)
            event["deterministic_reverification"] = deepcopy(reverified)
            event["verification"] = deepcopy(reverified)
        else:
            reverified = plan["verification"]
        _transition(event, "verified", attempt_at)
        event["verification"] = deepcopy(reverified)

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
            "candidate_id": plan.get("candidate_id"),
            "selector": event.get("selector"),
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
                "candidate_id": plan.get("candidate_id"),
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
                "candidate_id": plan.get("candidate_id"),
                "selector": event.get("selector"),
                "selection_reason_codes": event.get("selection_reason_codes", []),
                "base_version": plan["base_version"],
                "final_version": updated["version"],
                "verification_passed": reverified["passed"],
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
