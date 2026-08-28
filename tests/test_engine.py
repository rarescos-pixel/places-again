import json
from pathlib import Path

from places_again.engine import (
    apply_plan,
    build_recovery_candidates,
    build_recovery_plan,
    create_call_sheets,
    reverify_recovery_plan,
    validate_schedule,
)


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
    assert plan["metrics"]["affected_activities"] == 3
    assert plan["metrics"]["activities_recovered"] == 3
    assert plan["metrics"]["shifted_minutes"] == 270
    assert plan["metrics"]["unaffected_activities_moved"] == 0
    assert plan["metrics"]["unresolved_activities"] == 0
    assert plan["metrics"]["person_hours_at_risk"] == 12.0
    assert plan["metrics"]["person_hours_restored"] == 12.0
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
    assert any(
        "Synthetic Cover Soprano B" == message["recipient"] for message in messages
    )


def test_validation_detects_person_conflicts():
    state = seed()
    state["sessions"][3]["start"] = "12:30"
    state["sessions"][3]["end"] = "13:15"
    result = validate_schedule(state)
    assert result["passed"] is False
    assert any(item["type"] == "person_conflict" for item in result["violations"])


def test_same_engine_recovers_commercial_shoot():
    state = json.loads(
        Path("data/scenarios/commercial_shoot.json").read_text(encoding="utf-8")
    )
    plan = build_recovery_plan(
        state,
        {
            "kind": "person_unavailable",
            "person_id": "dp_principal",
            "start": "07:00",
            "end": "16:00",
            "reason": "same-day illness",
        },
    )
    assert plan["safe_to_commit"] is True
    assert plan["metrics"]["affected_activities"] == 4
    assert plan["metrics"]["activities_recovered"] == 4
    assert plan["metrics"]["person_hours_restored"] == 26.0
    assert plan["metrics"]["unaffected_activities_moved"] == 0
    assert {action["new_person_id"] for action in plan["actions"]} == {
        "dp_cover_early"
    }


def test_multiple_safe_candidates_expose_a_real_operational_tradeoff():
    state = seed()
    result = build_recovery_candidates(
        state, disruption(), plan_id="plan-1234567890abcdef"
    )

    assert len(result["candidates"]) >= 2
    first, second = result["candidates"][:2]
    assert all(candidate["verification"]["passed"] for candidate in (first, second))
    assert first["metrics"]["highest_priority_activities_moved"] == 0
    assert second["metrics"]["shifted_minutes"] < first["metrics"]["shifted_minutes"]
    assert second["metrics"]["highest_priority_activities_moved"] > 0
    assert second["metrics"]["people_schedule_changed"] > first["metrics"]["people_schedule_changed"]


def test_commercial_candidates_trade_continuity_for_cover_workload_balance():
    state = json.loads(
        Path("data/scenarios/commercial_shoot.json").read_text(encoding="utf-8")
    )
    result = build_recovery_candidates(
        state,
        {
            "kind": "person_unavailable",
            "person_id": "dp_principal",
            "start": "07:00",
            "end": "16:00",
            "reason": "same-day illness",
        },
        plan_id="plan-abcdef1234567890",
    )

    assert len(result["candidates"]) == 2
    continuity, balanced = result["candidates"]
    assert continuity["metrics"]["qualified_covers_used"] == 1
    assert balanced["metrics"]["qualified_covers_used"] == 2
    assert balanced["metrics"]["maximum_cover_minutes"] < continuity["metrics"][
        "maximum_cover_minutes"
    ]
    assert balanced["metrics"]["people_schedule_changed"] > continuity["metrics"][
        "people_schedule_changed"
    ]
    assert all(candidate["verification"]["passed"] for candidate in result["candidates"])


def test_reverification_rejects_a_candidate_that_overrides_qualification():
    state = seed()
    plan = build_recovery_plan(state, disruption())
    plan["actions"][0]["new_person_id"] = "pianist"
    plan["safe_to_commit"] = True

    proof = reverify_recovery_plan(state, plan)
    assert proof["passed"] is False
    assert any(item["type"] == "unqualified_cover" for item in proof["violations"])
    try:
        apply_plan(state, plan)
    except ValueError as error:
        assert "re-verification" in str(error).lower()
    else:
        raise AssertionError("tampered candidate bypassed deterministic safety")


def test_reverification_rejects_reassigning_the_disrupted_person_to_themself():
    state = seed()
    plan = build_recovery_plan(state, disruption())
    for action in plan["actions"]:
        action["new_person_id"] = "soprano_principal"
    plan["safe_to_commit"] = True

    proof = reverify_recovery_plan(state, plan)

    assert proof["passed"] is False
    assert proof["checks"]["disrupted_person_removed"] is False
    assert any(
        item["type"] == "disrupted_person_reassigned"
        for item in proof["violations"]
    )
    try:
        apply_plan(state, plan)
    except ValueError as error:
        assert "re-verification" in str(error).lower()
    else:
        raise AssertionError("self-replacement bypassed deterministic safety")


def test_reverification_rejects_an_action_outside_the_exact_schema():
    state = seed()
    plan = build_recovery_plan(state, disruption())
    plan["actions"][0]["untrusted_field"] = "ignore safety"
    plan["safe_to_commit"] = True

    proof = reverify_recovery_plan(state, plan)

    assert proof["passed"] is False
    assert proof["checks"]["action_schema_valid"] is False
    assert any(item["type"] == "invalid_action_schema" for item in proof["violations"])


def test_reverification_rejects_an_unknown_action_type():
    state = seed()
    plan = build_recovery_plan(state, disruption())
    plan["actions"][0]["type"] = "replace_and_notify"
    plan["safe_to_commit"] = True

    proof = reverify_recovery_plan(state, plan)

    assert proof["passed"] is False
    assert proof["checks"]["action_schema_valid"] is False
    assert any(item["type"] == "invalid_action_type" for item in proof["violations"])
