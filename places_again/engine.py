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


DEFAULT_SOFT_PRIORITIES = [
    {
        "code": "preserve_highest_priority_activity",
        "description": "Preserve the timing of the highest-priority activity when a safe alternative exists.",
        "rank": 1,
    },
    {
        "code": "minimize_people_schedule_changes",
        "description": "Change as few people's working schedules as possible.",
        "rank": 2,
    },
    {
        "code": "minimize_shifted_minutes",
        "description": "Minimize total schedule movement after higher operational priorities are protected.",
        "rank": 3,
    },
    {
        "code": "minimize_resource_rescheduling",
        "description": "Avoid moving scarce rooms, stages, locations, or equipment.",
        "rank": 4,
    },
    {
        "code": "balance_cover_workload",
        "description": "Avoid concentrating every recovered activity on one qualified cover.",
        "rank": 5,
    },
]


def operational_soft_priorities(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return visible, non-safety preferences supplied to the Gemini selector."""
    priorities = state.get("soft_priorities", DEFAULT_SOFT_PRIORITIES)
    return sorted(deepcopy(priorities), key=lambda item: (item.get("rank", 99), item["code"]))


def _candidate_plan_id(base_plan_id: str | None, index: int) -> str:
    base = (base_plan_id or f"plan-{uuid4().hex[:16]}").removeprefix("plan-")
    safe_hex = "".join(character for character in base.lower() if character in "0123456789abcdef")
    if len(safe_hex) < 8:
        safe_hex = uuid4().hex[:16]
    return f"plan-{safe_hex[:28]}{index:02x}"[:37]


def _assignment_options(
    state: dict[str, Any],
    scheduled: list[dict[str, Any]],
    activity: dict[str, Any],
    missing_person_id: str,
    covers: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Enumerate hard-constraint-safe assignments for one affected activity."""
    duration = _minutes(activity["end"]) - _minutes(activity["start"])
    activity_resources = _resources(activity)
    options: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any]]] = []
    for cover in covers:
        participants = [
            cover["id"] if person == missing_person_id else person
            for person in activity["participants"]
        ]
        for start_minutes in range(7 * 60, 20 * 60 - duration + 1, 15):
            start = _clock(start_minutes)
            end = _clock(start_minutes + duration)
            if any(
                not _resource_available(state, resource_id, start, end)
                for resource_id in activity_resources
            ):
                continue
            if _resource_busy(scheduled, activity_resources, start, end, activity["id"]):
                continue
            if not _participants_available(
                state, scheduled, participants, start, end, activity["id"]
            ):
                continue

            assigned = deepcopy(activity)
            assigned["participants"] = participants
            assigned["start"] = start
            assigned["end"] = end
            shift = abs(start_minutes - _minutes(activity["start"]))
            moved = shift > 0
            action = {
                "type": "replace_and_move" if moved else "replace_person",
                "activity_id": activity["id"],
                "session_id": activity["id"],
                "old_person_id": missing_person_id,
                "new_person_id": cover["id"],
                "old_start": activity["start"],
                "new_start": start,
                "old_end": activity["end"],
                "new_end": end,
                "reason": (
                    "qualified cover assigned in a conflict-free alternative slot"
                    if moved
                    else "qualified cover assigned in the original slot"
                ),
            }
            option_key = (
                shift,
                len(participants) if moved else 2,
                len(activity_resources) if moved else 0,
                cover["name"],
                start,
            )
            options.append((option_key, assigned, action))
    options.sort(key=lambda item: item[0])
    return [(assigned, action) for _, assigned, action in options]


def _action_costs(
    actions: list[dict[str, Any]],
    affected_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    highest_priority = max(
        (activity.get("priority", 0) for activity in affected_by_id.values()),
        default=0,
    )
    shifted_minutes = 0
    priority_weighted_shifted_minutes = 0
    highest_priority_moved = 0
    activities_moved = 0
    people_changed: set[str] = set()
    resources_rescheduled: set[str] = set()
    cover_minutes: dict[str, int] = {}
    for action in actions:
        activity = affected_by_id[action["activity_id"]]
        duration = _minutes(action["new_end"]) - _minutes(action["new_start"])
        cover_id = action["new_person_id"]
        cover_minutes[cover_id] = cover_minutes.get(cover_id, 0) + duration
        shift = abs(_minutes(action["new_start"]) - _minutes(action["old_start"]))
        people_changed.update([action["old_person_id"], action["new_person_id"]])
        shifted_minutes += shift
        priority_weighted_shifted_minutes += shift * activity.get("priority", 0)
        if shift:
            activities_moved += 1
            people_changed.update(activity["participants"])
            resources_rescheduled.update(_resources(activity))
            if activity.get("priority", 0) == highest_priority:
                highest_priority_moved += 1
    return {
        "shifted_minutes": shifted_minutes,
        "priority_weighted_shifted_minutes": priority_weighted_shifted_minutes,
        "highest_priority_activities_moved": highest_priority_moved,
        "activities_moved": activities_moved,
        "people_schedule_changed": len(people_changed),
        "resources_rescheduled": len(resources_rescheduled),
        "maximum_cover_minutes": max(cover_minutes.values(), default=0),
        "qualified_covers_used": len(cover_minutes),
        "collateral_disruption_score": (
            len(people_changed)
            + len(resources_rescheduled)
            + activities_moved
            + (highest_priority_moved * 4)
        ),
    }


def _strategy_cost(costs: dict[str, Any], strategy: str) -> tuple[Any, ...]:
    if strategy == "balance_cover_workload":
        return (
            costs["maximum_cover_minutes"],
            costs["highest_priority_activities_moved"],
            costs["people_schedule_changed"],
            costs["shifted_minutes"],
        )
    if strategy == "minimize_shift":
        return (
            costs["shifted_minutes"],
            costs["highest_priority_activities_moved"],
            costs["people_schedule_changed"],
            costs["priority_weighted_shifted_minutes"],
        )
    if strategy == "minimize_people":
        return (
            costs["people_schedule_changed"],
            costs["highest_priority_activities_moved"],
            costs["shifted_minutes"],
            costs["resources_rescheduled"],
        )
    if strategy == "preserve_resources":
        return (
            costs["resources_rescheduled"],
            costs["highest_priority_activities_moved"],
            costs["people_schedule_changed"],
            costs["shifted_minutes"],
        )
    return (
        costs["highest_priority_activities_moved"],
        costs["priority_weighted_shifted_minutes"],
        costs["people_schedule_changed"],
        costs["shifted_minutes"],
    )


def _project_plan_state(state: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    projected = deepcopy(state)
    activity_map = {activity["id"]: activity for activity in _activities(projected)}
    for action in plan["actions"]:
        if action["type"] == "human_decision_required":
            continue
        activity = activity_map[action["activity_id"]]
        activity["participants"] = [
            action["new_person_id"]
            if person == action["old_person_id"]
            else person
            for person in activity["participants"]
        ]
        activity["start"] = action["new_start"]
        activity["end"] = action["new_end"]
    return projected


def reverify_recovery_plan(
    state: dict[str, Any], plan: dict[str, Any]
) -> dict[str, Any]:
    """Re-prove every hard invariant from current state, not plan claims."""
    violations: list[dict[str, str]] = []
    required_action_fields = {
        "type",
        "activity_id",
        "session_id",
        "old_person_id",
        "new_person_id",
        "old_start",
        "new_start",
        "old_end",
        "new_end",
        "reason",
    }
    allowed_action_types = {"replace_person", "replace_and_move"}
    disruption = plan.get("disruption", {})
    missing_person_id = disruption.get("person_id")
    current_by_id = {activity["id"]: activity for activity in _activities(state)}
    affected_ids = {
        activity["id"]
        for activity in _activities(state)
        if missing_person_id in activity["participants"]
        and _overlaps(
            activity["start"],
            activity["end"],
            disruption.get("start", "00:00"),
            disruption.get("end", "00:00"),
        )
    }
    action_ids: list[str] = []
    actions = plan.get("actions", [])
    if not isinstance(actions, list):
        violations.append({"type": "invalid_action_schema", "activity_id": "multiple"})
        actions = []
    for action in actions:
        if not isinstance(action, dict):
            violations.append({"type": "invalid_action_schema", "activity_id": "multiple"})
            continue
        activity_id = action.get("activity_id", "")
        action_ids.append(activity_id)
        if set(action) != required_action_fields or not all(
            isinstance(action.get(field), str) and action[field]
            for field in required_action_fields
        ):
            violations.append({"type": "invalid_action_schema", "activity_id": activity_id})
            continue
        if action["type"] not in allowed_action_types or action["session_id"] != activity_id:
            violations.append({"type": "invalid_action_type", "activity_id": activity_id})
            continue
        activity = current_by_id.get(activity_id)
        if activity is None or activity_id not in affected_ids:
            violations.append({"type": "unexpected_activity", "activity_id": activity_id})
            continue
        if (
            action.get("old_person_id") != missing_person_id
            or action.get("old_start") != activity["start"]
            or action.get("old_end") != activity["end"]
        ):
            violations.append({"type": "action_state_mismatch", "activity_id": activity_id})
        if action["new_person_id"] == missing_person_id:
            violations.append(
                {"type": "disrupted_person_reassigned", "activity_id": activity_id}
            )
        moved = (
            action["new_start"] != action["old_start"]
            or action["new_end"] != action["old_end"]
        )
        if (action["type"] == "replace_person" and moved) or (
            action["type"] == "replace_and_move" and not moved
        ):
            violations.append({"type": "invalid_action_type", "activity_id": activity_id})
        cover = state["people"].get(action.get("new_person_id"))
        missing = state["people"].get(missing_person_id)
        if cover is None or missing is None or not set(missing.get("skills", [])).issubset(
            set(cover.get("skills", []))
        ):
            violations.append({"type": "unqualified_cover", "activity_id": activity_id})
        try:
            original_duration = _minutes(activity["end"]) - _minutes(activity["start"])
            proposed_duration = _minutes(action["new_end"]) - _minutes(action["new_start"])
        except (KeyError, TypeError, ValueError):
            violations.append({"type": "invalid_time", "activity_id": activity_id})
        else:
            if original_duration != proposed_duration or proposed_duration <= 0:
                violations.append({"type": "duration_changed", "activity_id": activity_id})

    if len(action_ids) != len(set(action_ids)):
        violations.append({"type": "duplicate_activity_action", "activity_id": "multiple"})
    if set(action_ids) != affected_ids:
        violations.append({"type": "affected_set_mismatch", "activity_id": "multiple"})
    if plan.get("base_version") != state.get("version"):
        violations.append({"type": "stale_plan", "activity_id": "state"})

    schedule_proof = {"passed": False, "checks": {}, "violations": []}
    if not violations:
        try:
            projected = _project_plan_state(state, plan)
            projected_by_id = {
                activity["id"]: activity for activity in _activities(projected)
            }
            for activity_id in affected_ids:
                if missing_person_id in projected_by_id[activity_id]["participants"]:
                    violations.append(
                        {
                            "type": "disrupted_person_still_assigned",
                            "activity_id": activity_id,
                        }
                    )
            if not violations:
                schedule_proof = validate_schedule(projected)
        except (KeyError, TypeError, ValueError):
            violations.append({"type": "invalid_plan_shape", "activity_id": "multiple"})
    violations.extend(schedule_proof.get("violations", []))
    violation_types = {item["type"] for item in violations}
    return {
        "passed": not violations,
        "checks": {
            "base_version_fresh": "stale_plan" not in violation_types,
            "affected_set_complete": "affected_set_mismatch" not in violation_types,
            "one_action_per_activity": "duplicate_activity_action" not in violation_types,
            "actions_match_current_state": "action_state_mismatch" not in violation_types,
            "action_schema_valid": not {
                "invalid_action_schema",
                "invalid_action_type",
            }.intersection(violation_types),
            "qualified_cover": "unqualified_cover" not in violation_types,
            "disrupted_person_removed": not {
                "disrupted_person_reassigned",
                "disrupted_person_still_assigned",
            }.intersection(violation_types),
            "duration_preserved": "duration_changed" not in violation_types,
            **schedule_proof.get("checks", {}),
        },
        "violations": violations,
    }


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


def _plan_metrics(
    state: dict[str, Any],
    affected: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    unresolved: list[str],
) -> dict[str, Any]:
    changed = [action for action in actions if action["type"] != "human_decision_required"]
    costs = _action_costs(changed, {activity["id"]: activity for activity in affected})
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
    changed_ids = {action["activity_id"] for action in changed}
    person_minutes_restored = sum(
        (_minutes(activity["end"]) - _minutes(activity["start"]))
        * len(activity["participants"])
        for activity in affected
        if activity["id"] in changed_ids
    )
    return {
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
        "shifted_minutes": costs["shifted_minutes"],
        "unaffected_activities_moved": 0,
        "unaffected_sessions_moved": 0,
        "unresolved_activities": len(unresolved),
        "unresolved": len(unresolved),
        **costs,
    }


def _build_candidate_plan(
    state: dict[str, Any],
    disruption: dict[str, Any],
    affected: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    *,
    plan_id: str,
) -> dict[str, Any]:
    plan = {
        "plan_id": plan_id,
        "base_version": state["version"],
        "scenario_id": state.get("scenario_id", "opera"),
        "disruption": deepcopy(disruption),
        "affected_activities": [activity["id"] for activity in affected],
        "affected_sessions": [activity["id"] for activity in affected],
        "actions": deepcopy(actions),
        "metrics": _plan_metrics(state, affected, actions, []),
        "verification": {},
        "safe_to_commit": True,
    }
    plan["verification"] = reverify_recovery_plan(state, plan)
    plan["safe_to_commit"] = plan["verification"]["passed"]
    return plan


def _human_required_plan(
    state: dict[str, Any],
    disruption: dict[str, Any],
    affected: list[dict[str, Any]],
    *,
    plan_id: str,
) -> dict[str, Any]:
    unresolved = [activity["id"] for activity in affected]
    actions = [
        {
            "type": "human_decision_required",
            "activity_id": activity_id,
            "session_id": activity_id,
            "reason": "no complete hard-constraint-safe recovery candidate exists",
        }
        for activity_id in unresolved
    ]
    return {
        "plan_id": plan_id,
        "base_version": state["version"],
        "scenario_id": state.get("scenario_id", "opera"),
        "disruption": deepcopy(disruption),
        "affected_activities": unresolved,
        "affected_sessions": unresolved,
        "actions": actions,
        "metrics": _plan_metrics(state, affected, actions, unresolved),
        "verification": {
            "passed": False,
            "checks": {"complete_safe_candidate": False},
            "violations": [
                {"type": "no_complete_safe_candidate", "activity_id": activity_id}
                for activity_id in unresolved
            ],
        },
        "safe_to_commit": False,
    }


def _action_signature(actions: list[dict[str, Any]]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        sorted(
            (
                action["activity_id"],
                action.get("new_person_id", ""),
                action.get("new_start", ""),
                action.get("new_end", ""),
            )
            for action in actions
        )
    )


PARETO_COSTS = (
    "highest_priority_activities_moved",
    "people_schedule_changed",
    "shifted_minutes",
    "resources_rescheduled",
    "maximum_cover_minutes",
)


def _pareto_frontier(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove metric-equivalent and dominated choices from the heuristic sample."""
    unique: dict[tuple[int, ...], dict[str, Any]] = {}
    for candidate in sorted(candidates, key=lambda item: _action_signature(item["actions"])):
        vector = tuple(candidate["metrics"][metric] for metric in PARETO_COSTS)
        unique.setdefault(vector, candidate)

    frontier = []
    for vector, candidate in unique.items():
        dominated = any(
            other_vector != vector
            and all(other <= current for other, current in zip(other_vector, vector))
            and any(other < current for other, current in zip(other_vector, vector))
            for other_vector in unique
        )
        if not dominated:
            frontier.append(candidate)
    return frontier


def build_recovery_candidates(
    state: dict[str, Any],
    disruption: dict[str, Any],
    *,
    plan_id: str | None = None,
    maximum_candidates: int = 5,
) -> dict[str, Any]:
    """Generate a small, diverse set of deterministically safe plans.

    Hard constraints define the feasible space. The returned candidates expose
    only soft operational trade-offs to a bounded model selector.
    """
    if disruption.get("kind") != "person_unavailable":
        raise ValueError("Only person_unavailable is supported")
    person_id = disruption["person_id"]
    if person_id not in state["people"]:
        raise ValueError(f"Unknown person: {person_id}")
    maximum_candidates = max(1, min(5, maximum_candidates))
    base_plan_id = plan_id or f"plan-{uuid4().hex[:16]}"
    all_activities = deepcopy(_activities(state))
    affected = [
        activity
        for activity in all_activities
        if person_id in activity["participants"]
        and _overlaps(
            activity["start"], activity["end"], disruption["start"], disruption["end"]
        )
    ]
    affected_ids = {activity["id"] for activity in affected}
    unaffected = [activity for activity in all_activities if activity["id"] not in affected_ids]
    covers = _qualified_covers(state, person_id)
    activity_order = sorted(
        affected,
        key=lambda activity: (-activity.get("priority", 0), activity["start"], activity["id"]),
    )
    affected_by_id = {activity["id"]: activity for activity in affected}
    strategies = [
        "preserve_priority",
        "minimize_shift",
        "minimize_people",
        "preserve_resources",
        "balance_cover_workload",
    ]
    generated: dict[tuple[tuple[str, ...], ...], dict[str, Any]] = {}

    if not affected:
        plan = _build_candidate_plan(
            state, disruption, affected, [], plan_id=_candidate_plan_id(base_plan_id, 1)
        )
        plan["candidate_id"] = "candidate-a"
        generated[_action_signature([])] = plan
    elif covers:
        beam = [{"scheduled": deepcopy(unaffected), "actions": []}]
        for activity in activity_order:
            expanded = []
            for partial in beam:
                options = _assignment_options(
                    state,
                    partial["scheduled"],
                    activity,
                    person_id,
                    covers,
                )
                for assigned, action in options[:18]:
                    actions = partial["actions"] + [action]
                    expanded.append(
                        {
                            "scheduled": partial["scheduled"] + [assigned],
                            "actions": actions,
                        }
                    )
            # Preserve the best frontier for every soft objective. This avoids
            # running the same feasibility search four times while retaining
            # genuine trade-offs instead of one weighted-score answer.
            next_beam = []
            next_signatures: set[tuple[tuple[str, ...], ...]] = set()
            for strategy in strategies:
                ranked = sorted(
                    expanded,
                    key=lambda partial: (
                        _strategy_cost(
                            _action_costs(partial["actions"], affected_by_id), strategy
                        ),
                        _action_signature(partial["actions"]),
                    ),
                )
                for partial in ranked[:24]:
                    signature = _action_signature(partial["actions"])
                    if signature in next_signatures:
                        continue
                    next_beam.append(partial)
                    next_signatures.add(signature)
            beam = next_beam[:96]
            if not beam:
                break

        final_partials = []
        final_signatures: set[tuple[tuple[str, ...], ...]] = set()
        for strategy in strategies:
            ranked = sorted(
                beam,
                key=lambda partial: (
                    _strategy_cost(
                        _action_costs(partial["actions"], affected_by_id), strategy
                    ),
                    _action_signature(partial["actions"]),
                ),
            )
            for partial in ranked[:12]:
                signature = _action_signature(partial["actions"])
                if signature in final_signatures:
                    continue
                final_partials.append(partial)
                final_signatures.add(signature)

        for partial in final_partials:
            candidate = _build_candidate_plan(
                state,
                disruption,
                affected,
                partial["actions"],
                plan_id=_candidate_plan_id(base_plan_id, 1),
            )
            if candidate["safe_to_commit"]:
                generated.setdefault(_action_signature(candidate["actions"]), candidate)

    all_safe = _pareto_frontier(list(generated.values()))
    selected: list[dict[str, Any]] = []
    selected_signatures: set[tuple[tuple[str, ...], ...]] = set()
    for strategy in strategies:
        if not all_safe:
            break
        best = min(
            all_safe,
            key=lambda candidate: (
                _strategy_cost(candidate["metrics"], strategy),
                _action_signature(candidate["actions"]),
            ),
        )
        signature = _action_signature(best["actions"])
        if signature not in selected_signatures:
            selected.append(deepcopy(best))
            selected_signatures.add(signature)
        if len(selected) == maximum_candidates:
            break

    if len(selected) < maximum_candidates:
        for candidate in sorted(
            all_safe,
            key=lambda item: (
                _strategy_cost(item["metrics"], "preserve_priority"),
                _action_signature(item["actions"]),
            ),
        ):
            signature = _action_signature(candidate["actions"])
            if signature in selected_signatures:
                continue
            selected.append(deepcopy(candidate))
            selected_signatures.add(signature)
            if len(selected) == maximum_candidates:
                break

    for index, candidate in enumerate(selected, start=1):
        candidate["candidate_id"] = f"candidate-{chr(96 + index)}"
        candidate["plan_id"] = _candidate_plan_id(base_plan_id, index)
        candidate["selection_evidence"] = {
            "highest_priority_activities_moved": candidate["metrics"]["highest_priority_activities_moved"],
            "people_schedule_changed": candidate["metrics"]["people_schedule_changed"],
            "shifted_minutes": candidate["metrics"]["shifted_minutes"],
            "resources_rescheduled": candidate["metrics"]["resources_rescheduled"],
            "maximum_cover_minutes": candidate["metrics"]["maximum_cover_minutes"],
            "qualified_covers_used": candidate["metrics"]["qualified_covers_used"],
            "collateral_disruption_score": candidate["metrics"]["collateral_disruption_score"],
        }

    fallback = _human_required_plan(
        state,
        disruption,
        affected,
        plan_id=_candidate_plan_id(base_plan_id, 0),
    )
    return {
        "candidate_set_id": f"set-{base_plan_id.removeprefix('plan-')[:24]}",
        "base_version": state["version"],
        "scenario_id": state.get("scenario_id", "opera"),
        "affected_activities": [activity["id"] for activity in affected],
        "soft_priorities": operational_soft_priorities(state),
        "candidates": selected,
        "fallback_plan": fallback,
    }


def build_recovery_plan(
    state: dict[str, Any],
    disruption: dict[str, Any],
    *,
    plan_id: str | None = None,
) -> dict[str, Any]:
    """Compatibility entry point: return the bounded deterministic first choice."""
    candidate_set = build_recovery_candidates(state, disruption, plan_id=plan_id)
    if candidate_set["candidates"]:
        return deepcopy(candidate_set["candidates"][0])
    return deepcopy(candidate_set["fallback_plan"])


def apply_plan(state: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Apply a verified plan to a matching base version."""
    if not plan["safe_to_commit"]:
        raise ValueError("Plan has unresolved activities and cannot be auto-committed")
    reverified = reverify_recovery_plan(state, plan)
    if not reverified["checks"].get("base_version_fresh", False):
        raise ValueError("Plan is stale: production state changed after simulation")
    if not reverified["passed"]:
        violation_types = sorted(
            {item["type"] for item in reverified.get("violations", [])}
        )
        raise ValueError(
            "Deterministic re-verification rejected the plan: "
            + ", ".join(violation_types)
        )

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
            "deterministic_reverification_passed": reverified["passed"],
            "candidate_id": plan.get("candidate_id"),
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
