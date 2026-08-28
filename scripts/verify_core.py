"""Dependency-free verification of the deterministic recovery boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from places_again.engine import (
    apply_plan,
    build_recovery_candidates,
    build_recovery_plan,
    create_call_sheets,
    reverify_recovery_plan,
    validate_schedule,
)
from places_again.repository import JsonRepository


def main() -> None:
    state = json.loads(
        (ROOT / "data" / "scenarios" / "opera.json").read_text(encoding="utf-8")
    )
    disruption = {
        "kind": "person_unavailable",
        "person_id": "soprano_principal",
        "start": "08:00",
        "end": "14:00",
        "reason": "same-day illness",
    }
    plan = build_recovery_plan(state, disruption)
    assert plan["safe_to_commit"] is True
    assert plan["metrics"]["affected_activities"] == 3
    assert plan["metrics"]["activities_recovered"] == 3
    assert plan["metrics"]["person_hours_at_risk"] == 12.0
    assert plan["metrics"]["person_hours_restored"] == 12.0
    assert plan["metrics"]["shifted_minutes"] == 270
    assert plan["metrics"]["unaffected_activities_moved"] == 0
    assert plan["metrics"]["unresolved_activities"] == 0
    updated = apply_plan(state, plan)
    assert updated["version"] == 2
    assert validate_schedule(updated)["passed"] is True
    messages = create_call_sheets(updated, plan, "en") + create_call_sheets(
        updated, plan, "ro"
    )
    assert len(messages) == 12
    assert all(message["status"] == "prepared_not_sent" for message in messages)

    candidates = build_recovery_candidates(
        state, disruption, plan_id="plan-1234567890abcdef"
    )["candidates"]
    assert len(candidates) == 2
    preserve_priority, reduce_shift = candidates
    assert preserve_priority["metrics"]["highest_priority_activities_moved"] == 0
    assert reduce_shift["metrics"]["shifted_minutes"] < preserve_priority["metrics"][
        "shifted_minutes"
    ]
    assert reduce_shift["metrics"]["people_schedule_changed"] > preserve_priority[
        "metrics"
    ]["people_schedule_changed"]
    assert all(reverify_recovery_plan(state, candidate)["passed"] for candidate in candidates)

    film_state = json.loads(
        (ROOT / "data" / "scenarios" / "commercial_shoot.json").read_text(
            encoding="utf-8"
        )
    )
    film_candidates = build_recovery_candidates(
        film_state,
        {
            "kind": "person_unavailable",
            "person_id": "dp_principal",
            "start": "07:00",
            "end": "16:00",
            "reason": "same-day illness",
        },
        plan_id="plan-abcdef1234567890",
    )["candidates"]
    assert len(film_candidates) == 2
    assert film_candidates[0]["metrics"]["qualified_covers_used"] == 1
    assert film_candidates[1]["metrics"]["qualified_covers_used"] == 2
    assert film_candidates[1]["metrics"]["maximum_cover_minutes"] < film_candidates[0][
        "metrics"
    ]["maximum_cover_minutes"]

    with TemporaryDirectory() as directory:
        repository = JsonRepository(Path(directory) / "state.json")

        def advance(current):
            current["version"] += 1
            return current, current["version"]

        assert repository.mutate(advance, "opera") == 2
        assert repository.load("opera")["version"] == 2

    print("core verification passed")


if __name__ == "__main__":
    main()
