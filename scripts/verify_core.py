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
    build_recovery_plan,
    create_call_sheets,
    validate_schedule,
)
from places_again.repository import JsonRepository


def main() -> None:
    state = json.loads((ROOT / "data" / "demo_state.json").read_text(encoding="utf-8"))
    disruption = {
        "kind": "person_unavailable",
        "person_id": "soprano_principal",
        "start": "08:00",
        "end": "14:00",
        "reason": "same-day illness",
    }
    plan = build_recovery_plan(state, disruption)
    assert plan["safe_to_commit"] is True
    assert plan["metrics"] == {
        "affected_sessions": 3,
        "changed_sessions": 3,
        "shifted_minutes": 270,
        "unaffected_sessions_moved": 0,
        "unresolved": 0,
    }
    updated = apply_plan(state, plan)
    assert updated["version"] == 2
    assert validate_schedule(updated)["passed"] is True
    messages = create_call_sheets(updated, plan, "en") + create_call_sheets(
        updated, plan, "ro"
    )
    assert len(messages) == 12
    assert all(message["status"] == "prepared_not_sent" for message in messages)

    with TemporaryDirectory() as directory:
        repository = JsonRepository(Path(directory) / "state.json")

        def advance(current):
            current["version"] += 1
            return current, current["version"]

        assert repository.mutate(advance) == 2
        assert repository.load()["version"] == 2

    print("core verification passed")


if __name__ == "__main__":
    main()
