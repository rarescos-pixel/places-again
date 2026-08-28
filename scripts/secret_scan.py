#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", "runtime", ".pytest_cache"}
PATTERNS = {
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "github_token": re.compile(
        r"(?:ghp_[0-9A-Za-z]{36,}|github_pat_[0-9A-Za-z_]{20,})"
    ),
    "aws_access_key": re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}"),
}


def _text_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    )
    return [
        ROOT / line
        for line in output.splitlines()
        if line and not EXCLUDED_PARTS.intersection(Path(line).parts)
    ]


def _scan_text(text: str, location: str) -> list[dict[str, str | int]]:
    findings = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append(
                    {"type": name, "location": location, "line": line_number}
                )
    return findings


def scan_worktree() -> list[dict[str, str | int]]:
    findings = []
    for path in _text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        findings.extend(_scan_text(text, str(path.relative_to(ROOT))))
    return findings


def scan_history() -> list[dict[str, str | int]]:
    findings = []
    revisions = subprocess.check_output(
        ["git", "rev-list", "--all"], cwd=ROOT, text=True
    ).splitlines()
    expression = (
        r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"
        r"|AIza[0-9A-Za-z_-]{35}"
        r"|ghp_[0-9A-Za-z]{36,}"
        r"|github_pat_[0-9A-Za-z_]{20,}"
        r"|(AKIA|ASIA)[0-9A-Z]{16}"
    )
    for revision in revisions:
        result = subprocess.run(
            [
                "git",
                "grep",
                "-I",
                "-n",
                "-E",
                "-e",
                expression,
                revision,
                "--",
                ".",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode not in {0, 1}:
            raise RuntimeError(result.stderr.strip() or "git history scan failed")
        for line in result.stdout.splitlines():
            findings.append(
                {"type": "history_pattern", "location": line.split(":", 2)[0:2], "line": 0}
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    worktree = scan_worktree()
    history = scan_history() if arguments.history else []
    report = {
        "worktree_files_scanned": len(_text_files()),
        "history_scanned": arguments.history,
        "findings": worktree + history,
        "passed": not worktree and not history,
    }
    rendered = json.dumps(report, indent=2)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
