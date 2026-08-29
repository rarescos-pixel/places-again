#!/usr/bin/env bash

# Read-only diagnosis for Cloud Run 404s that occur only outside Google Cloud.
# Does not mutate Cloud Run, IAM, Firestore, Pub/Sub, Vertex AI, or org policies.

set -Eeuo pipefail

readonly DEFAULT_PROJECT_ID="project-2ee12060-728f-434f-9ad"
readonly REGION="europe-west1"
readonly SERVICE="places-again"
PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT:-${DEFAULT_PROJECT_ID}}}"

note() { printf '[Places, Again][public-404-diagnostic] %s\n' "$*"; }
section() { printf '\n== %s ==\n' "$1"; }

command -v gcloud >/dev/null 2>&1 || { note "STOP: gcloud is required."; exit 2; }
command -v python3 >/dev/null 2>&1 || { note "STOP: python3 is required."; exit 2; }

ACTIVE_ACCOUNT="$(gcloud auth list --filter='status:ACTIVE' --limit=1 --format='value(account)')"
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"

section "Identity and project"
note "project=${PROJECT_ID}"
note "project_number=${PROJECT_NUMBER}"
note "account=${ACTIVE_ACCOUNT}"
gcloud projects get-ancestors "${PROJECT_ID}" --format='table(type,id)' || true

section "Effective Cloud Run service front door"
gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='yaml(status.url,status.address,metadata.annotations,spec.template.metadata.annotations)' || true

INGRESS="$(gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(metadata.annotations."run.googleapis.com/ingress")' 2>/dev/null || true)"
DEFAULT_DISABLED="$(gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(metadata.annotations."run.googleapis.com/default-url-disabled")' 2>/dev/null || true)"
INVOKER_DISABLED="$(gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(metadata.annotations."run.googleapis.com/invoker-iam-disabled")' 2>/dev/null || true)"
STATUS_URL="$(gcloud run services describe "${SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)' 2>/dev/null || true)"
note "effective_ingress=${INGRESS:-unset}"
note "default_url_disabled=${DEFAULT_DISABLED:-false}"
note "invoker_iam_disabled=${INVOKER_DISABLED:-false}"
note "status_url=${STATUS_URL:-unset}"

section "Effective organization policies"
for constraint in \
  constraints/run.allowedIngress \
  constraints/run.managed.requireInvokerIam \
  constraints/iam.allowedPolicyMemberDomains; do
  echo "--- ${constraint} ---"
  gcloud org-policies describe "${constraint}" \
    --project="${PROJECT_ID}" --effective --format=yaml 2>&1 || true
done

section "Cloud Run HttpIngress policy audit"
POLICY_LOG="/tmp/places-again-http-ingress-policy.json"
FILTER="resource.type=\"audited_resource\" AND log_name=\"projects/${PROJECT_ID}/logs/cloudaudit.googleapis.com%2Fpolicy\" AND resource.labels.method=\"run.googleapis.com/HttpIngress\""
gcloud logging read "${FILTER}" \
  --project="${PROJECT_ID}" --freshness=3h --limit=50 --format=json > "${POLICY_LOG}" 2>/tmp/places-again-log-error.txt || true

python3 - "${POLICY_LOG}" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
try:
    rows = json.loads(path.read_text(encoding='utf-8') or '[]')
except Exception as exc:
    print(f'POLICY_LOG_PARSE_ERROR={exc}')
    rows = []

print(f'HTTP_INGRESS_POLICY_LOG_COUNT={len(rows)}')
text = json.dumps(rows, ensure_ascii=False).lower()
keywords = {
    'vpc_service_controls': ['vpc service controls', 'vpc_service_controls', 'service perimeter'],
    'no_matching_access_level': ['no_matching_access_level', 'no matching access level'],
    'organization_policy': ['organization policy', 'org policy'],
    'ingress_denial': ['httpingress', 'ingress'],
}
for label, needles in keywords.items():
    print(f'{label.upper()}_SIGNAL={any(n in text for n in needles)}')

for idx, row in enumerate(rows[:5], 1):
    compact = json.dumps(row, ensure_ascii=False)
    interesting = {}
    for key in ('severity', 'timestamp', 'resource', 'protoPayload', 'jsonPayload'):
        if key in row:
            interesting[key] = row[key]
    print(f'POLICY_EVENT_{idx}=' + json.dumps(interesting, ensure_ascii=False)[:4000])
PY

if [[ -s /tmp/places-again-log-error.txt ]]; then
  note "logging_query_stderr=$(tr '\n' ' ' < /tmp/places-again-log-error.txt | head -c 1200)"
fi

section "Owner-environment HTTP check"
if [[ -n "${STATUS_URL}" ]]; then
  HTTP_CODE="$(curl --silent --show-error --location --output /tmp/places-again-owner-body \
    --write-out '%{http_code}' --max-time 30 "${STATUS_URL}/api/capabilities" || true)"
  note "owner_environment_http=${HTTP_CODE}"
fi

section "Diagnostic summary"
if [[ "${INGRESS}" != "all" ]]; then
  note "DIAGNOSIS=EFFECTIVE_INGRESS_NOT_ALL"
elif [[ "${DEFAULT_DISABLED,,}" == "true" ]]; then
  note "DIAGNOSIS=DEFAULT_URL_DISABLED"
elif [[ "${INVOKER_DISABLED,,}" != "true" ]]; then
  note "DIAGNOSIS=INVOKER_IAM_CHECK_STILL_ENABLED"
else
  if python3 - "${POLICY_LOG}" <<'PY'
import json, pathlib, sys
rows = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8') or '[]')
text = json.dumps(rows).lower()
raise SystemExit(0 if any(x in text for x in ('vpc service controls','vpc_service_controls','service perimeter','no_matching_access_level')) else 1)
PY
  then
    note "DIAGNOSIS=VPC_SERVICE_CONTROLS_OR_ACCESS_CONTEXT_BLOCK"
  elif [[ -s "${POLICY_LOG}" ]] && [[ "$(cat "${POLICY_LOG}")" != "[]" ]]; then
    note "DIAGNOSIS=POLICY_LEVEL_HTTP_INGRESS_BLOCK_REVIEW_EVENTS_ABOVE"
  else
    note "DIAGNOSIS=NO_POLICY_DENIAL_FOUND_REQUIRES_DEEPER_CLOUD_RUN_ENDPOINT_CHECK"
  fi
fi

note "FINAL_STATUS=PUBLIC_404_DIAGNOSTIC_COMPLETE"
