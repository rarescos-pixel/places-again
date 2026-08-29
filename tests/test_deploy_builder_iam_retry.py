from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def _deployer() -> str:
    return (ROOT / "deploy.sh").read_text(encoding="utf-8")


def _retry_function() -> str:
    deployer = _deployer()
    start = deployer.index("run_source_deploy_with_builder_iam_retry() {")
    end = deployer.index("\n}\n\nassert_config_equals", start) + 2
    return deployer[start:end]


def test_source_deploy_retries_only_the_known_builder_iam_propagation_failure():
    deployer = _deployer()

    assert "run_source_deploy_with_builder_iam_retry()" in deployer
    assert "storage\\.objects\\.get" in deployer
    assert "BUILD_IAM_PROPAGATION_RETRY=" in deployer
    assert "max_attempts=5" in deployer
    assert "delay_seconds > 60" in deployer


def test_public_api_source_deploy_uses_the_builder_iam_retry_gate():
    deployer = _deployer()

    assert (
        'run_source_deploy_with_builder_iam_retry gcloud run deploy "${API_SERVICE}"'
        in deployer
    )
    assert 'grant_project_role "serviceAccount:${BUILD_SA}" \'roles/run.builder\'' in deployer


def test_retry_preserves_the_real_gcloud_exit_code_and_logs_each_attempt():
    deployer = _deployer()

    assert "exit_code=${PIPESTATUS[0]}" in deployer
    assert 'return "${exit_code}"' in deployer
    assert "source-deploy-${TIMESTAMP}-attempt-${attempt}.log" in deployer


def test_transient_storage_permission_failure_is_retried_until_success(tmp_path):
    state = tmp_path / "attempts"
    runner = tmp_path / "runner.sh"
    runner.write_text(
        f"""#!/usr/bin/env bash
set -Eeuo pipefail
REPORT_DIR={tmp_path!s}
TIMESTAMP=test
note() {{ printf '%s\\n' "$1"; }}
sleep() {{ :; }}
{_retry_function()}
fake_deploy() {{
  local count=0
  [[ -f {state!s} ]] && count="$(cat {state!s})"
  count=$((count + 1))
  printf '%s' "${{count}}" > {state!s}
  if (( count < 3 )); then
    echo "build service account does not have storage.objects.get access"
    return 13
  fi
  echo "deployment succeeded"
}}
run_source_deploy_with_builder_iam_retry fake_deploy
[[ "$(cat {state!s})" == "3" ]]
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        ["bash", str(runner)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "BUILD_IAM_PROPAGATION_RETRY=1" in completed.stdout
    assert "BUILD_IAM_PROPAGATION_RETRY=2" in completed.stdout
    assert "BUILD_IAM_PROPAGATION=ready attempt=3" in completed.stdout
