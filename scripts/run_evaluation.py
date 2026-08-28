#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from places_again.engine import apply_plan, build_recovery_plan
from places_again.models import IncidentRequest
from places_again.repository import JsonRepository
from places_again.workflow import process_event, receive_incident


CASES_PATH = ROOT / "evaluation" / "cases.json"


def _apply_setup(state: dict[str, Any], operations: list[dict[str, Any]]) -> None:
    for operation in operations:
        kind = operation["op"]
        if kind == "set_person_skills":
            state["people"][operation["person_id"]]["skills"] = operation["value"]
        elif kind == "set_person_availability":
            state["people"][operation["person_id"]]["availability"] = operation["value"]
        elif kind == "set_resource_availability":
            state["resources"][operation["resource_id"]]["availability"] = operation["value"]
        elif kind == "add_person":
            state["people"][operation["person_id"]] = operation["value"]
        elif kind == "add_person_skill":
            state["people"][operation["person_id"]]["skills"].append(operation["value"])
        elif kind == "add_activity":
            state["activities"].append(operation["value"])
        elif kind == "add_activity_resource":
            activity = next(
                item for item in state["activities"] if item["id"] == operation["activity_id"]
            )
            activity["resources"].append(operation["value"])
        else:
            raise ValueError(f"unsupported setup operation: {kind}")


def _evaluate_case(case: dict[str, Any], directory: Path) -> dict[str, Any]:
    repository = JsonRepository(directory / f"{case['id']}.json")
    scenario_id = case["scenario_id"]
    setup = case.get("setup", [])
    if setup:
        def configure(state):
            _apply_setup(state, setup)
            return state, None

        repository.mutate(configure, scenario_id)

    before = repository.snapshot(scenario_id)
    base_version = before["version"]
    try:
        request = IncidentRequest.model_validate(
            {
                "scenario_id": scenario_id,
                "disruption": case["disruption"],
                "source": "evaluation",
            }
        )
    except ValidationError as error:
        outcome = "validation_rejected"
        return {
            "id": case["id"],
            "labels": case["labels"],
            "expected": case["expected"],
            "actual": outcome,
            "passed": outcome == case["expected"],
            "validation_errors": len(error.errors()),
            "invariants": {
                "unsafe_commit": False,
                "unresolved_auto_commit": False,
                "duplicate_side_effect": False,
                "accepted_plan_failed_verification": False,
            },
        }

    disruption = request.disruption.model_dump()
    delivery = case.get("delivery", "once")
    if delivery == "stale_plan":
        plan = build_recovery_plan(before, disruption)
        changed = deepcopy(before)
        changed["version"] += 1
        try:
            apply_plan(changed, plan)
        except ValueError as error:
            outcome = "stale_rejected" if "stale" in str(error).lower() else "wrong_error"
        else:
            outcome = "stale_accepted"
        return {
            "id": case["id"],
            "labels": case["labels"],
            "expected": case["expected"],
            "actual": outcome,
            "passed": outcome == case["expected"],
            "invariants": {
                "unsafe_commit": outcome == "stale_accepted",
                "unresolved_auto_commit": False,
                "duplicate_side_effect": False,
                "accepted_plan_failed_verification": False,
            },
        }

    event = receive_incident(
        scenario_id,
        disruption,
        event_id=uuid4(),
        source="evaluation",
        repository=repository,
    )
    if delivery == "concurrent":
        second = receive_incident(
            scenario_id,
            disruption,
            event_id=uuid4(),
            source="evaluation",
            repository=repository,
        )
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda item: process_event(item, repository=repository),
                    [event["event_id"], second["event_id"]],
                )
            )
        outcome = (
            "concurrent_safe"
            if sum(item.get("outcome") == "autonomous_safe_commit" for item in results) == 1
            and sum(item.get("outcome") == "no_affected_activities" for item in results) == 1
            else "concurrent_unsafe"
        )
        result = next(
            (item for item in results if item.get("plan")), results[0]
        )
    else:
        crash_map = {
            "crash_after_plan": "after_plan",
            "crash_before_commit": "before_commit",
            "crash_after_commit_before_completion": "after_commit_before_completion",
        }
        if delivery in crash_map:
            try:
                process_event(
                    event["event_id"],
                    repository=repository,
                    crash_at=crash_map[delivery],
                )
            except RuntimeError:
                pass
        result = process_event(event["event_id"], repository=repository)
        outcome = result.get("outcome")
        if result.get("failure", {}).get("type") == "invalid_or_unknown_incident":
            outcome = "human_required_invalid"
        if delivery == "duplicate":
            process_event(event["event_id"], repository=repository)

    after = repository.snapshot(scenario_id)
    outbox_ids = [message["id"] for message in after.get("outbox", [])]
    plan = result.get("plan", {})
    metrics = plan.get("metrics", {})
    version_delta = after["version"] - base_version
    invariants = {
        "unsafe_commit": outcome == "autonomous_safe_commit"
        and not plan.get("safe_to_commit", False),
        "unresolved_auto_commit": outcome == "autonomous_safe_commit"
        and metrics.get("unresolved_activities", 0) > 0,
        "duplicate_side_effect": version_delta > 1 or len(outbox_ids) != len(set(outbox_ids)),
        "accepted_plan_failed_verification": outcome == "autonomous_safe_commit"
        and not plan.get("verification", {}).get("passed", False),
    }
    return {
        "id": case["id"],
        "labels": case["labels"],
        "expected": case["expected"],
        "actual": outcome,
        "passed": outcome == case["expected"] and not any(invariants.values()),
        "status": result.get("status"),
        "version_delta": version_delta,
        "outbox_count": len(outbox_ids),
        "metrics": metrics,
        "invariants": invariants,
    }


def run_evaluation(cases_path: Path = CASES_PATH) -> dict[str, Any]:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="places-again-eval-") as directory:
        results = [_evaluate_case(case, Path(directory)) for case in cases]
    stale = [result for result in results if "stale_plan" in result["labels"]]
    accepted = [
        result for result in results if result["actual"] == "autonomous_safe_commit"
    ]
    invariant_totals = {
        key: sum(result["invariants"][key] for result in results)
        for key in next(iter(results))["invariants"]
    }
    return {
        "case_count": len(results),
        "passed": sum(result["passed"] for result in results),
        "failed": sum(not result["passed"] for result in results),
        "domains": sorted({case["scenario_id"] for case in cases}),
        "acceptance_targets": {
            "unsafe_commits": invariant_totals["unsafe_commit"],
            "unresolved_auto_commits": invariant_totals["unresolved_auto_commit"],
            "duplicate_side_effects": invariant_totals["duplicate_side_effect"],
            "stale_plan_rejection_rate": (
                round(
                    100
                    * sum(result["actual"] == "stale_rejected" for result in stale)
                    / len(stale),
                    1,
                )
                if stale
                else None
            ),
            "accepted_plans_passing_verification_rate": (
                round(
                    100
                    * sum(
                        not result["invariants"]["accepted_plan_failed_verification"]
                        for result in accepted
                    )
                    / len(accepted),
                    1,
                )
                if accepted
                else None
            ),
        },
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--summary", action="store_true", help="Print totals instead of every case"
    )
    arguments = parser.parse_args()
    report = run_evaluation(arguments.cases)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered + "\n", encoding="utf-8")
    if arguments.summary:
        print(
            json.dumps(
                {key: value for key, value in report.items() if key != "results"},
                indent=2,
            )
        )
    else:
        print(rendered)
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
