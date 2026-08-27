from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
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


def _person_available(person: dict[str, Any], start: str, end: str) -> bool:
    return any(
        _minutes(window["start"]) <= _minutes(start)
        and _minutes(window["end"]) >= _minutes(end)
        for window in person.get("availability", [])
    )


def _busy(
    sessions: list[dict[str, Any]],
    person_id: str,
    start: str,
    end: str,
    ignored_session_id: str,
) -> bool:
    return any(
        session["id"] != ignored_session_id
        and person_id in session["participants"]
        and session.get("status", "scheduled") == "scheduled"
        and _overlaps(start, end, session["start"], session["end"])
        for session in sessions
    )


def _room_busy(
    sessions: list[dict[str, Any]],
    room: str,
    start: str,
    end: str,
    ignored_session_id: str,
) -> bool:
    return any(
        session["id"] != ignored_session_id
        and session["room"] == room
        and session.get("status", "scheduled") == "scheduled"
        and _overlaps(start, end, session["start"], session["end"])
        for session in sessions
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
    sessions: list[dict[str, Any]],
    participants: list[str],
    start: str,
    end: str,
    ignored_session_id: str,
) -> bool:
    for person_id in participants:
        person = state["people"][person_id]
        if not _person_available(person, start, end):
            return False
        if _busy(sessions, person_id, start, end, ignored_session_id):
            return False
    return True


def _find_slot(
    state: dict[str, Any],
    sessions: list[dict[str, Any]],
    session: dict[str, Any],
    participants: list[str],
) -> tuple[str, str] | None:
    duration = _minutes(session["end"]) - _minutes(session["start"])
    original_start = _minutes(session["start"])
    candidates = []
    for start_minutes in range(8 * 60, 19 * 60 - duration + 1, 15):
        start = _clock(start_minutes)
        end = _clock(start_minutes + duration)
        if _room_busy(sessions, session["room"], start, end, session["id"]):
            continue
        if not _participants_available(
            state, sessions, participants, start, end, session["id"]
        ):
            continue
        candidates.append((abs(start_minutes - original_start), start, end))
    if not candidates:
        return None
    _, start, end = min(candidates)
    return start, end


def validate_schedule(state: dict[str, Any]) -> dict[str, Any]:
    """Return machine-readable proof that the current schedule is conflict-free."""
    violations: list[dict[str, str]] = []
    sessions = [
        session
        for session in state["sessions"]
        if session.get("status", "scheduled") == "scheduled"
    ]

    for session in sessions:
        for person_id in session["participants"]:
            person = state["people"].get(person_id)
            if person is None:
                violations.append(
                    {
                        "type": "unknown_person",
                        "session_id": session["id"],
                        "person_id": person_id,
                    }
                )
            elif not _person_available(person, session["start"], session["end"]):
                violations.append(
                    {
                        "type": "outside_availability",
                        "session_id": session["id"],
                        "person_id": person_id,
                    }
                )

    for index, first in enumerate(sessions):
        for second in sessions[index + 1 :]:
            if not _overlaps(first["start"], first["end"], second["start"], second["end"]):
                continue
            if first["room"] == second["room"]:
                violations.append(
                    {
                        "type": "room_conflict",
                        "session_id": first["id"],
                        "other_session_id": second["id"],
                    }
                )
            shared_people = sorted(set(first["participants"]) & set(second["participants"]))
            for person_id in shared_people:
                violations.append(
                    {
                        "type": "person_conflict",
                        "session_id": first["id"],
                        "other_session_id": second["id"],
                        "person_id": person_id,
                    }
                )

    violation_types = {item["type"] for item in violations}
    return {
        "passed": not violations,
        "checks": {
            "known_people": "unknown_person" not in violation_types,
            "participant_availability": "outside_availability" not in violation_types,
            "rooms_conflict_free": "room_conflict" not in violation_types,
            "people_conflict_free": "person_conflict" not in violation_types,
        },
        "violations": violations,
    }


def build_recovery_plan(
    state: dict[str, Any], disruption: dict[str, Any]
) -> dict[str, Any]:
    """Create a policy-bounded low-change plan without mutating state."""
    if disruption.get("kind") != "person_unavailable":
        raise ValueError("Only person_unavailable is supported in the prototype")
    person_id = disruption["person_id"]
    if person_id not in state["people"]:
        raise ValueError(f"Unknown person: {person_id}")

    sessions = deepcopy(state["sessions"])
    affected = [
        session
        for session in sessions
        if person_id in session["participants"]
        and _overlaps(
            session["start"], session["end"], disruption["start"], disruption["end"]
        )
    ]
    covers = _qualified_covers(state, person_id)
    actions: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for session in affected:
        options: list[tuple[int, str, str, str, dict[str, Any], list[str]]] = []
        for cover in covers:
            participants = [
                cover["id"] if participant == person_id else participant
                for participant in session["participants"]
            ]
            slot = _find_slot(state, sessions, session, participants)
            if slot:
                new_start, new_end = slot
                shift = abs(_minutes(new_start) - _minutes(session["start"]))
                options.append(
                    (shift, cover["name"], new_start, new_end, cover, participants)
                )

        if options:
            _, _, new_start, new_end, cover, participants = min(options)
            moved = new_start != session["start"]
            actions.append(
                {
                    "type": "replace_and_move" if moved else "replace_person",
                    "session_id": session["id"],
                    "old_person_id": person_id,
                    "new_person_id": cover["id"],
                    "old_start": session["start"],
                    "new_start": new_start,
                    "old_end": session["end"],
                    "new_end": new_end,
                    "reason": (
                        "qualified cover required the nearest conflict-free slot"
                        if moved
                        else "qualified cover available in the original slot"
                    ),
                }
            )
            session["participants"] = participants
            session["start"] = new_start
            session["end"] = new_end
        else:
            unresolved.append(session["id"])
            actions.append(
                {
                    "type": "human_decision_required",
                    "session_id": session["id"],
                    "reason": "no qualified cover and conflict-free slot found",
                }
            )

    shifted_minutes = sum(
        abs(_minutes(action["new_start"]) - _minutes(action["old_start"]))
        for action in actions
        if "new_start" in action
    )
    projected_state = deepcopy(state)
    projected_state["sessions"] = sessions
    verification = validate_schedule(projected_state)
    return {
        "plan_id": f"plan-{uuid4().hex[:8]}",
        "base_version": state["version"],
        "disruption": disruption,
        "affected_sessions": [session["id"] for session in affected],
        "actions": actions,
        "metrics": {
            "affected_sessions": len(affected),
            "changed_sessions": len([a for a in actions if a["type"] != "human_decision_required"]),
            "shifted_minutes": shifted_minutes,
            "unaffected_sessions_moved": 0,
            "unresolved": len(unresolved),
        },
        "verification": verification,
        "safe_to_commit": not unresolved and verification["passed"],
    }


def apply_plan(state: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """Apply a previously generated plan and return a new state."""
    if plan["base_version"] != state["version"]:
        raise ValueError("Plan is stale: production state changed after simulation")
    if not plan["safe_to_commit"]:
        raise ValueError("Plan has unresolved sessions and cannot be auto-committed")

    updated = deepcopy(state)
    sessions = {session["id"]: session for session in updated["sessions"]}
    for action in plan["actions"]:
        session = sessions[action["session_id"]]
        session["participants"] = [
            action["new_person_id"] if participant == action["old_person_id"] else participant
            for participant in session["participants"]
        ]
        session["start"] = action["new_start"]
        session["end"] = action["new_end"]
        session["revision_reason"] = action["reason"]

    updated["version"] += 1
    updated.setdefault("audit", []).append(
        {
            "event": "recovery_plan_committed",
            "plan_id": plan["plan_id"],
            "from_version": state["version"],
            "to_version": updated["version"],
            "actions": len(plan["actions"]),
            "verification_passed": plan["verification"]["passed"],
            "action_details": deepcopy(plan["actions"]),
        }
    )
    return updated


def create_call_sheets(
    state: dict[str, Any], plan: dict[str, Any], language: str = "en"
) -> list[dict[str, Any]]:
    changed_ids = {action["session_id"] for action in plan["actions"]}
    changed_sessions = [s for s in state["sessions"] if s["id"] in changed_ids]
    messages = []
    for person_id, person in state["people"].items():
        relevant = [s for s in changed_sessions if person_id in s["participants"]]
        if not relevant:
            continue
        lines = [
            f"{session['start']}–{session['end']} · {session['title']} · {session['room']}"
            for session in sorted(relevant, key=lambda item: item["start"])
        ]
        if language == "ro":
            subject = f"Program revizuit — {state['production']}"
            body = "Programul tău actualizat:\n" + "\n".join(lines) + "\nTe rugăm să confirmi primirea."
        else:
            subject = f"Revised call — {state['production']}"
            body = "Your updated call:\n" + "\n".join(lines) + "\nPlease acknowledge receipt."
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
