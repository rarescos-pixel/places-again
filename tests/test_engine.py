import json
from pathlib import Path

from places_again.engine import apply_plan, build_recovery_plan, create_call_sheets, validate_schedule


def seed():
    return json.loads(Path("data/demo_state.json").read_text(encoding="utf-8"))


def disruption():
    return {
        "kind": "person_unavailable",
        "person_id": "soprano_principal",
        "start": "08:00",
        "end": "14:00",
        "reason": "same-day illness",
    }


def test_recovery_is_safe_and_minimal():
    plan = build_recovery_plan(seed(), disruption())
    assert plan["safe_to_commit"] is True
    assert plan["metrics"] == {
        "affected_sessions": 3,
        "changed_sessions": 3,
        "shifted_minutes": 270,
        "unaffected_sessions_moved": 0,
        "unresolved": 0,
    }
    assert plan["verification"]["passed"] is True
    assert {action["new_person_id"] for action in plan["actions"]} == {"soprano_cover"}


def test_commit_changes_version_and_preserves_unaffected_session():
    original = seed()
    plan = build_recovery_plan(original, disruption())
    updated = apply_plan(original, plan)
    assert original["version"] == 1
    assert updated["version"] == 2
    untouched_before = next(s for s in original["sessions"] if s["id"] == "s3")
    untouched_after = next(s for s in updated["sessions"] if s["id"] == "s3")
    assert untouched_after == untouched_before


def test_stale_plan_is_rejected():
    original = seed()
    plan = build_recovery_plan(original, disruption())
    original["version"] = 2
    try:
        apply_plan(original, plan)
    except ValueError as error:
        assert "stale" in str(error).lower()
    else:
        raise AssertionError("stale plan was accepted")


def test_call_sheets_are_prepared_not_sent():
    original = seed()
    plan = build_recovery_plan(original, disruption())
    updated = apply_plan(original, plan)
    messages = create_call_sheets(updated, plan, "ro")
    assert messages
    assert all(message["status"] == "prepared_not_sent" for message in messages)
    assert any("Ana Pop" == message["recipient"] for message in messages)


def test_validation_detects_person_conflicts():
    state = seed()
    state["sessions"][3]["start"] = "12:30"
    state["sessions"][3]["end"] = "13:15"
    result = validate_schedule(state)
    assert result["passed"] is False
    assert any(item["type"] == "person_conflict" for item in result["violations"])
