from __future__ import annotations

from copy import deepcopy
from typing import Any

from places_again.engine import apply_plan, build_recovery_plan, create_call_sheets
from places_again.repository import repository


def _find_plan(state: dict[str, Any], plan_id: str) -> dict[str, Any] | None:
    record = state.get("recovery_plans", {}).get(plan_id)
    if not record:
        return None
    return record["plan"]


def get_current_schedule() -> dict[str, Any]:
    """Return the current production version, people, sessions, and audit events."""
    return repository.snapshot()


def get_audit_log() -> dict[str, Any]:
    """Return the immutable-style action log and unsent outbox."""
    state = repository.snapshot()
    return {"version": state["version"], "audit": state.get("audit", []), "outbox": state.get("outbox", [])}


def analyze_person_disruption(
    person_id: str, start: str, end: str, reason: str
) -> dict[str, Any]:
    """Simulate a person outage and return a policy-bounded recovery plan."""
    disruption = {
        "kind": "person_unavailable",
        "person_id": person_id,
        "start": start,
        "end": end,
        "reason": reason,
    }

    def preview(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        plan = build_recovery_plan(state, disruption)
        state.setdefault("recovery_plans", {})[plan["plan_id"]] = {
            "status": "previewed",
            "plan": plan,
        }
        state.setdefault("audit", []).append(
            {
                "event": "recovery_plan_previewed",
                "plan_id": plan["plan_id"],
                "base_version": plan["base_version"],
                "safe_to_commit": plan["safe_to_commit"],
            }
        )
        return state, deepcopy(plan)

    return repository.mutate(preview)


def commit_recovery_plan(plan_id: str) -> dict[str, Any]:
    """Commit a safe, non-stale recovery plan. Never sends messages."""
    def commit(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        plan = _find_plan(state, plan_id)
        if plan is None:
            return state, {"status": "error", "message": "unknown plan_id"}
        record = state.get("recovery_plans", {}).get(plan_id, {})
        if record.get("status") == "committed":
            return state, {
                "status": "already_committed",
                "plan_id": plan_id,
                "new_version": record.get("committed_version"),
                "state": deepcopy(state),
            }
        try:
            updated = apply_plan(state, plan)
        except ValueError as error:
            return state, {"status": "error", "message": str(error)}
        updated.setdefault("recovery_plans", {})[plan_id] = {
            "status": "committed",
            "committed_version": updated["version"],
            "plan": plan,
        }
        return updated, {
            "status": "committed",
            "plan_id": plan_id,
            "new_version": updated["version"],
            "state": deepcopy(updated),
        }

    return repository.mutate(commit)


def prepare_call_sheets(plan_id: str, language: str = "en") -> dict[str, Any]:
    """Prepare, but do not send, call sheets for people affected by a plan."""
    if language not in {"en", "ro"}:
        return {"status": "error", "message": "language must be en or ro"}

    def prepare(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        plan = _find_plan(state, plan_id)
        if plan is None:
            return state, {"status": "error", "message": "unknown plan_id"}
        record = state.get("recovery_plans", {}).get(plan_id, {})
        if record.get("status") != "committed":
            return state, {
                "status": "error",
                "message": "plan must be committed before preparing call sheets",
            }
        messages = create_call_sheets(state, plan, language)
        existing_ids = {message["id"] for message in state.get("outbox", [])}
        new_messages = [message for message in messages if message["id"] not in existing_ids]
        state.setdefault("outbox", []).extend(new_messages)
        if new_messages:
            state.setdefault("audit", []).append(
                {
                    "event": "call_sheets_prepared",
                    "plan_id": plan_id,
                    "language": language,
                    "count": len(new_messages),
                    "delivery_status": "prepared_not_sent",
                }
            )
        return state, {
            "status": "prepared_not_sent",
            "count": len(messages),
            "messages": deepcopy(messages),
        }

    return repository.mutate(prepare)


def reset_demo() -> dict[str, Any]:
    """Reset the synthetic demo production to its original state."""
    return repository.reset()
