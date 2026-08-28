from __future__ import annotations

import os
from pathlib import Path
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts" / "enable_google_apis.sh"


def _write_fake_gcloud(tmp_path: Path, behavior: str) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "calls.log"
    attempts = tmp_path / "attempts"
    script = bin_dir / "gcloud"
    script.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env bash
            set -u
            printf '%s\\n' "$*" >> "${{FAKE_GCLOUD_CALLS}}"

            if [[ "$1 $2" == "services list" ]]; then
              printf '%s\\n' run.googleapis.com cloudbuild.googleapis.com
              exit 0
            fi

            if [[ "$1 $2" == "services enable" ]]; then
              count=0
              [[ -f "${{FAKE_GCLOUD_ATTEMPTS}}" ]] && count="$(<"${{FAKE_GCLOUD_ATTEMPTS}}")"
              count=$((count + 1))
              printf '%s' "${{count}}" > "${{FAKE_GCLOUD_ATTEMPTS}}"
              {behavior}
            fi

            printf 'unexpected fake gcloud invocation: %s\\n' "$*" >&2
            exit 90
            """
        ),
        encoding="utf-8",
    )
    script.chmod(0o755)
    return bin_dir, calls


def _run_helper(tmp_path: Path, behavior: str, *apis: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    bin_dir, calls = _write_fake_gcloud(tmp_path, behavior)
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bin_dir}:{env['PATH']}",
            "FAKE_GCLOUD_CALLS": str(calls),
            "FAKE_GCLOUD_ATTEMPTS": str(tmp_path / "attempts"),
            "PLACES_AGAIN_API_RETRY_BASE_SECONDS": "0",
            "PLACES_AGAIN_API_RETRY_CAP_SECONDS": "0",
            "PLACES_AGAIN_API_RETRY_JITTER_SECONDS": "0",
            "PLACES_AGAIN_API_ENABLE_PACING_SECONDS": "0",
        }
    )
    quoted_apis = " ".join(apis)
    result = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{HELPER}"; enable_google_apis test-project {quoted_apis}',
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    call_lines = calls.read_text(encoding="utf-8").splitlines()
    return result, call_lines


def test_api_activation_skips_enabled_and_retries_429(tmp_path: Path) -> None:
    result, calls = _run_helper(
        tmp_path,
        'if [[ "${count}" -eq 1 ]]; then printf "ERROR 429: quota exceeded per minute\\n" >&2; exit 1; fi; exit 0',
        "run.googleapis.com",
        "aiplatform.googleapis.com",
    )

    assert result.returncode == 0, result.stderr
    assert calls[0].startswith("services list --enabled")
    assert not any("enable run.googleapis.com" in call for call in calls)
    assert sum("enable aiplatform.googleapis.com" in call for call in calls) == 2
    assert "result=retry retryable=true" in result.stdout
    assert "api=run.googleapis.com state=already_enabled action=skip" in result.stdout
    assert "api=aiplatform.googleapis.com state=enabled action=complete" in result.stdout


def test_api_activation_does_not_retry_non_transient_failure(tmp_path: Path) -> None:
    result, calls = _run_helper(
        tmp_path,
        'printf "PERMISSION_DENIED: caller lacks serviceusage.services.enable\\n" >&2; exit 7',
        "firestore.googleapis.com",
    )

    assert result.returncode == 7
    assert sum("enable firestore.googleapis.com" in call for call in calls) == 1
    assert "retryable=false" in result.stdout
    assert "PERMISSION_DENIED" in result.stderr


def test_each_missing_api_is_enabled_in_its_own_request(tmp_path: Path) -> None:
    result, calls = _run_helper(
        tmp_path,
        "exit 0",
        "firestore.googleapis.com",
        "pubsub.googleapis.com",
        "aiplatform.googleapis.com",
    )

    assert result.returncode == 0, result.stderr
    enable_calls = [call for call in calls if call.startswith("services enable")]
    assert enable_calls == [
        "services enable firestore.googleapis.com --project=test-project --quiet",
        "services enable pubsub.googleapis.com --project=test-project --quiet",
        "services enable aiplatform.googleapis.com --project=test-project --quiet",
    ]
