#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = [
    "README.md",
    "SECURITY.md",
    "FAILURE_MODES.md",
    "JUDGE_EVIDENCE.md",
    "docs/architecture.svg",
    "docs/workflow.svg",
    "docs/demo-script.md",
    "docs/submission.md",
    "docs/build-article.md",
    "docs/social-post.md",
    "evaluation/cases.json",
    "reports/evaluation-report.json",
    "reports/secret-scan.json",
    "scripts/cloud_e2e_test.py",
]
PLACEHOLDERS = [
    "[ADD CLOUD RUN URL AFTER E2E PASSES]",
    "[ADD PUBLIC YOUTUBE OR VIMEO URL]",
    "[ADD AFTER PUBLICATION]",
]


def check_local() -> dict:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
    evaluation = json.loads(
        (ROOT / "reports" / "evaluation-report.json").read_text(encoding="utf-8")
    )
    secrets = json.loads(
        (ROOT / "reports" / "secret-scan.json").read_text(encoding="utf-8")
    )
    tests = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "pytest"), "-q"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    targets = evaluation["acceptance_targets"]
    return {
        "required_files_present": not missing,
        "missing_files": missing,
        "tests_pass": tests.returncode == 0,
        "test_summary": tests.stdout.splitlines()[0] if tests.stdout else tests.stderr,
        "evaluation_pass": evaluation["failed"] == 0
        and evaluation["case_count"] >= 40,
        "evaluation_cases": evaluation["case_count"],
        "unsafe_commits": targets["unsafe_commits"],
        "unresolved_auto_commits": targets["unresolved_auto_commits"],
        "duplicate_side_effects": targets["duplicate_side_effects"],
        "stale_rejection_rate": targets["stale_plan_rejection_rate"],
        "accepted_verification_rate": targets[
            "accepted_plans_passing_verification_rate"
        ],
        "secret_scan_pass": secrets["passed"],
    }


def check_external() -> dict:
    evidence_paths = sorted((ROOT / "runtime").glob("cloud-e2e-evidence-*.json"))
    cloud = None
    if evidence_paths:
        cloud = json.loads(evidence_paths[-1].read_text(encoding="utf-8"))
    submission = (ROOT / "docs" / "submission.md").read_text(encoding="utf-8")
    remaining = [placeholder for placeholder in PLACEHOLDERS if placeholder in submission]
    return {
        "cloud_evidence_path": (
            str(evidence_paths[-1].relative_to(ROOT)) if evidence_paths else None
        ),
        "cloud_e2e_pass": bool(cloud and cloud.get("passed")),
        "submission_placeholders": remaining,
        "submission_links_complete": not remaining,
        "manual_checks": [
            "Repository access verified for judges",
            "Public video is English/subtitled and <= 4:00",
            "Entrant eligibility and employer-policy attestations completed",
            "Devpost category and prize selections match the submitted build",
            "Submitted commit tagged and deployed version frozen",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    local = check_local()
    external = {} if arguments.local_only else check_external()
    local_pass = (
        local["required_files_present"]
        and local["tests_pass"]
        and local["evaluation_pass"]
        and local["unsafe_commits"] == 0
        and local["unresolved_auto_commits"] == 0
        and local["duplicate_side_effects"] == 0
        and local["stale_rejection_rate"] == 100.0
        and local["accepted_verification_rate"] == 100.0
        and local["secret_scan_pass"]
    )
    external_pass = arguments.local_only or (
        external["cloud_e2e_pass"] and external["submission_links_complete"]
    )
    report = {
        "local": local,
        "external": external,
        "local_pass": local_pass,
        "external_automated_pass": external_pass,
        "passed": local_pass and external_pass,
    }
    rendered = json.dumps(report, indent=2)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
