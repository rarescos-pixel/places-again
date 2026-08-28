from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any
from uuid import uuid4


TIME_FORMAT = "%H:%M"


def _minutes(value: str) -> int:
    parsed = datetime.strptime(value, TIME_FORMAT)
    return parsed.hour * 60 + parsed.minute


def _clock(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _overlaps(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    return _minutes(start_a) < _minutes(end_b) and _minutes(start_b) < _minutes(end_a)


def _activities(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the v2 generic activities or a v1 sessions compatibility view."""
    return state.get("activities", state.get("sessions", []))


def _activity_key(state: dict[str, Any]) -> str:
    return "activities" if "activities" in state else "sessions"


def _resources(activity: dict[str, Any]) -> list[str]:
    if "resources" in activity:
        return activity["resources"]
    return [activity["room"]] if activity.get("room") else []


def _resource_name(state: dict[str, Any], resource_id: str) -> str:
    record = state.get("resources", {}).get(resource_id, {})
    return record.get("name", resource_id)


def _window_contains(windows: list[dict[str, str]], start: str, end: str) -> bool:
    return any(
        _minutes(window["start"]) <= _minutes(start)
        and _minutes(window["end"]) >= _minutes(end)
        for window in windows
    )


def _person_available(person: dict[str, Any], start: str, end: str) -> bool:
    return _window_contains(person.get("availability", []), start, end)


def _resource_available(
    state: dict[str, Any], resource_id: str, start: str, end: str
) -> bool:
    catalog = state.get("resources")
    if catalog is None:
        return True
    resource = catalog.get(resource_id)
    if resource is None:
        return False
    return _window_contains(resource.get("availability", []), start, end)


def _person_busy(
    activities: list[dict[str, Any]],
    person_id: str,
    start: str,
    end: str,
    ignored_activity_id: str,
) -> bool:
    return any(
        activity["id"] != ignored_activity_id
        and person_id in activity["participants"]
        and activity.get("status", "scheduled") == "scheduled"
        and _overlaps(start, end, activity["start"], activity["end"])
        for activity in activities
    )


def _resource_busy(
    activities: list[dict[str, Any]],
    resources: list[str],
    start: str,
    end: str,
    ignored_activity_id: str,
) -> bool:
    requested = set(resources)
    return any(
        activity["id"] != ignored_activity_id
        and requested.intersection(_resources(activity))
        and activity.get("status", "scheduled") == "scheduled"
        and _overlaps(start, end, activity["start"], activity["end"])
        for activity in activities
    )


def _qualified_covers(
    state: dict[str, Any], missing_person_id: str
) -> list[dict[str, Any]]:
    people = state["people"]
    missing = people[missing_person_id]
    required_skills = set(missing.get("skills", []))
    candidates = []
    for person_id, person in people.items():
        if person_id == missing_person_id:
            continue
        candidate_skills = set(person.get("skills", []))
        if required_skills.issubset(candidate_skills):
            candidates.append({"id": person_id, **person})
    return sorted(candidates, key=lambda candidate: candidate["name"])


def _participants_available(
    state: dict[str, Any],
    activities: list[dict[str, Any]],
    participants: list[str],
    start: str,
    end: str,
    ignored_activity_id: str,
) -> bool:
    for person_id in participants:
        person = state["people"].get(person_id)
        if person is None or not _person_available(person, start, end):
            return False
        if _person_busy(activities, person_id, start, end, ignored_activity_id):
            return False
    return True


def _find_slot(
    state: dict[str, Any],
    activities: list[dict[str, Any]],
    activity: dict[str, Any],
    participants: list[str],
) -> tuple[str, str] | None:
    duration = _minutes(activity["end"]) - _minutes(activity["start"])
    original_start = _minutes(activity["start"])
    activity_resources = _resources(activity)
    candidates = []
    for start_minutes in range(7 * 60, 20 * 60 - duration + 1, 15):
        start = _clock(start_minutes)
        end = _clock(start_minutes + duration)
        if any(
            not _resource_available(state, resource_id, start, end)
            for resource_id in activity_resources
        ):
            continue
        if _resource_busy(
            activities,
            activity_resources,
            start,
            end,
            activity["id"],
        ):
            continue
        if not _participants_available(
            state, activities, participants, start, end, activity["id"]
        ):
            continue
        candidates.append((abs(start_minutes - original_start), start, end))
    if not candidates:
        return None
    _, start, end = min(candidates)
    return start, end


def validate_schedule(state: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic, machine-readable safety proof."""
    violations: list[dict[str, str]] = []
    activities = [
        activity
        for activity in _activities(state)
        if activity.get("status", "scheduled") == "scheduled"
    ]

    for activity in activities:
        for person_id in activity["participants"]:
            person = state["people"].get(person_id)
            if person is None:
                violations.append(
                    {
                        "type": "unknown_person",
                        "activity_id": activity["id"],
                        "person_id": person_id,
                    }
                )
            elif not _person_available(person, activity["start"], activity["end"]):
                violations.append(
                    {
                        "type": "outside_availability",
                        "activity_id": activity["id"],
                        "person_id": person_id,
                    }
                )
        for resource_id in _resources(activity):
            if state.get("resources") is not None and resource_id not in state["resources"]:
                violations.append(
                    {
                        "type": "unknown_resource",
                        "activity_id": activity["id"],
                        "resource_id": resource_id,
                    }
                )
            elif not _resource_available(
                state, resource_id, activity["start"], activity["end"]
            ):
                violations.append(
                    {
                        "type": "resource_outside_availability",
                        "activity_id": activity["id"],
                        "resource_id": resource_id,
                    }
                )

    for index, first in enumerate(activities):
        for second in activities[index + 1 :]:
            if not _overlaps(
                first["start"], first["end"], second["start"], second["end"]
            ):
                continue
            for resource_id in sorted(
                set(_resources(first)).intersection(_resources(second))
            ):
                violations.append(
                    {
                        "type": "resource_conflict",
                        "activity_id": first["id"],
                        "other_activity_id": second["id"],
                        "resource_id": resource_id,
                    }
                )
            for person_id in sorted(
                set(first["participants"]).intersection(second["participants"])
            ):
                violations.append(
                    {
                        "type": "person_conflict",
                        "activity_id": first["id"],
                        "other_activity_id": second["id"],
                        "person_id": person_id,
                    }
                )

    violation_types = {item["type"] for item in violations}
    return {
        "passed": not violations,
        "checks": {
            "known_people": "unknown_person" not in violation_types,
            "participant_availability": "outside_availability" not in violation_types,
            "known_resources": "unknown_resource" not in violation_types,
            "resource_availability": "resource_outside_availability"
            not in violation_types,
            "resources_conflict_free": "resource_conflict" not in violation_types,
            "people_conflict_free": "person_conflict" not in violation_types,
        },
        "violations": violations,
    }


def build_recovery_plan(
    state: dict[str, Any],
    disruption: dict[str, Any],
    *,
    plan_id: str | None = None,
) -> dict[str, Any]:
    """Create a policy-bounded minimum-change plan without mutating state."""
    if disruption.get("kind") != "person_unavailable":
        raise ValueError("Only person_unavailable is supported")
    person_id = disruption["person_id"]
    if person_id not in state["people"]:
        raise ValueError(f"Unknown person: {person_id}")

    activities = deepcopy(_activities(state))
    affected = [
        activity
        for activity in activities
        if person_id in activity["participants"]
        and _overlaps(
            activity["start"], activity["end"], disruption["start"], disruption["end"]
        )
    ]
    covers = _qualified_covers(state, person_id)
    actions: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for activity in affected:
        options: list[tuple[int, str, str, str, dict[str, Any], list[str]]] = []
        for cover in covers:
            participants = [
                cover["id"] if participant == person_id else participant
                for participant in activity["participants"]
            ]
            slot = _find_slot(state, activities, activity, participants)
            if slot:
                new_start, new_end = slot
                shift = abs(_minutes(new_start) - _minutes(activity["start"]))
                options.append(
                    (shift, cover["name"], new_start, new_end, cover, participants)
                )

        if options:
            _, _, new_start, new_end, cover, participants = min(options)
            moved = new_start != activity["start"]
            actions.append(
                {
                    "type": "replace_and_move" if moved else "replace_person",
                    "activity_id": activity["id"],
                    "session_id": activity["id"],
                    "old_person_id": person_id,
                    "new_person_id": cover["id"],
                    "old_start": activity["start"],
                    "new_start": new_start,
                    "old_end": activity["end"],
                    "new_end": new_end,
                    "reason": (
                        "qualified cover required the nearest conflict-free slot"
                        if moved
                        else "qualified cover available in the original slot"
                    ),
                }
            )
            activity["participants"] = participants
            activity["start"] = new_start
            activity["end"] = new_end
        else:
            unresolved.append(activity["id"])
            actions.append(
                {
                    "type": "human_decision_required",
                    "activity_id": activity["id"],
                    "session_id": activity["id"],
                    "reason": "no qualified cover and conflict-free slot found",
                }
            )

    projected_state = deepcopy(state)
    projected_state[_activity_key(state)] = activities
    verification = validate_schedule(projected_state)
    changed = [
        action for action in actions if action["type"] != "human_decision_required"
    ]
    changed_ids = {action["activity_id"] for action in changed}
    shifted_minutes = sum(
        abs(_minutes(action["new_start"]) - _minutes(action["old_start"]))
        for action in changed
    )
    affected_people = sorted(
        {person for activity in affected for person in activity["participants"]}
    )
    affected_resources = sorted(
        {resource for activity in affected for resource in _resources(activity)}
    )
    person_minutes_at_risk = sum(
        (_minutes(activity["end"]) - _minutes(activity["start"]))
        * len(activity["participants"])
        for activity in affected
    )
    person_minutes_restored = sum(
        (_minutes(activity["end"]) - _minutes(activity["start"]))
        * len(activity["participants"])
        for activity in activities
        if activity["id"] in changed_ids
    )
    metrics = {
        "affected_activities": len(affected),
        "affected_sessions": len(affected),
        "affected_people": len(affected_people),
        "affected_resources": len(affected_resources),
        "person_minutes_at_risk": person_minutes_at_risk,
        "person_hours_at_risk": round(person_minutes_at_risk / 60, 2),
        "activities_recovered": len(changed),
        "changed_sessions": len(changed),
        "person_minutes_restored": person_minutes_restored,
        "person_hours_restored": round(person_minutes_restored / 60, 2),
        "shifted_minutes": shifted_minutes,
        "unaffected_activities_moved": 0,
        "unaffected_sessions_moved": 0,
        "unresolved_activities": len(unresolved),
        "unresolved": len(unresolved),
    }
    return {
        "plan_id": plan_id or f"plan-{uuid4().hex[:8]}",
        "base_version": state["version"],
        "scenario_id": state.get("scenario_id", "opera"),
        "disruption": deepcopy(disruption),
        "affected_activities": [activity["id"] for activity in affected],
        "affected_sessions": [activity["id"] for activity in affected],
        "actions": actions,
        "metrics": metrics,
        "verification": verification,
        "safe_to_commit": not unresolved and verification["passed"],
    }


def apply_plan(state: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Apply a verified plan to a matching base version."""
    if plan["base_version"] != state["version"]:
        raise ValueError("Plan is stale: production state changed after simulation")
    if not plan["safe_to_commit"]:
        raise ValueError("Plan has unresolved activities and cannot be auto-committed")

    updated = deepcopy(state)
    activities = {
        activity["id"]: activity for activity in _activities(updated)
    }
    for action in plan["actions"]:
        if action["type"] == "human_decision_required":
            continue
        activity = activities[action["activity_id"]]
        activity["participants"] = [
            action["new_person_id"]
            if participant == action["old_person_id"]
            else participant
            for participant in activity["participants"]
        ]
        activity["start"] = action["new_start"]
        activity["end"] = action["new_end"]
        activity["revision_reason"] = action["reason"]

    final_verification = validate_schedule(updated)
    if not final_verification["passed"]:
        raise ValueError("Safety invariant failed after applying plan")
    updated["version"] += 1
    updated.setdefault("audit", []).append(
        {
            "event": "recovery_plan_committed",
            "plan_id": plan["plan_id"],
            "from_version": state["version"],
            "to_version": updated["version"],
            "actions": len(plan["actions"]),
            "verification_passed": final_verification["passed"],
            "action_details": deepcopy(plan["actions"]),
        }
    )
    return updated


def create_call_sheets(
    state: dict[str, Any], plan: dict[str, Any], language: str = "en"
) -> list[dict[str, Any]]:
    changed_ids = {
        action["activity_id"]
        for action in plan["actions"]
        if action["type"] != "human_decision_required"
    }
    changed_activities = [
        activity for activity in _activities(state) if activity["id"] in changed_ids
    ]
    messages = []
    for person_id, person in state["people"].items():
        relevant = [
            activity
            for activity in changed_activities
            if person_id in activity["participants"]
        ]
        if not relevant:
            continue
        lines = [
            f"{activity['start']}–{activity['end']} · {activity['title']} · "
            + ", ".join(
                _resource_name(state, resource_id)
                for resource_id in _resources(activity)
            )
            for activity in sorted(relevant, key=lambda item: item["start"])
        ]
        if language == "ro":
            subject = f"Program revizuit — {state['production']}"
            body = (
                "Programul tău actualizat:\n"
                + "\n".join(lines)
                + "\nTe rugăm să confirmi primirea."
            )
        else:
            subject = f"Revised operations call — {state['production']}"
            body = (
                "Your updated call:\n"
                + "\n".join(lines)
                + "\nPlease acknowledge receipt."
            )
        messages.append(
            {
                "id": f"{plan['plan_id']}-{language}-{person_id}",
                "plan_id": plan["plan_id"],
                "recipient_id": person_id,
                "recipient": person["name"],
                "channel": "outbox",
                "language": language,
                "subject": subject,
                "body": body,
                "status": "prepared_not_sent",
            }
        )
    return messages
