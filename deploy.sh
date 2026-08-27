#!/usr/bin/env bash

# Places, Again — one-command Google Cloud recovery and deployment.
#
# This script is intentionally non-interactive. It diagnoses the previous
# regional build, applies the safe IAM/API fixes needed for a Cloud Run source
# deployment, deploys once (with one bounded retry), smoke-tests the public
# service, and leaves a timestamped report under runtime/.

set -Eeuo pipefail

readonly DEFAULT_PROJECT_ID="project-2ee12060-728f-434f-9ad"
readonly SERVICE_NAME="places-again"
readonly REGION="europe-west1"
readonly FIRESTORE_LOCATION="europe-west1"
readonly MODEL="gemini-3.5-flash"

PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT:-${DEFAULT_PROJECT_ID}}}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${SCRIPT_DIR}/runtime"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="${REPORT_DIR}/deployment-report-${TIMESTAMP}.txt"
LATEST_REPORT="${REPORT_DIR}/deployment-report-latest.txt"
DEPLOY_OUTPUT="${REPORT_DIR}/deploy-output-${TIMESTAMP}.txt"

mkdir -p "${REPORT_DIR}"
touch "${REPORT}"
exec > >(tee -a "${REPORT}") 2>&1

section() {
  printf '\n== %s ==\n' "$1"
}

note() {
  printf '%s\n' "$1"
}

die() {
  local message="$1"
  local code="${2:-1}"
  note "STOP: ${message}"
  exit "${code}"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1" 2
}

capture_build() {
  local location="$1"
  local label="$2"
  local build_id

  section "${label}: latest Cloud Build in ${location}"
  build_id="$(gcloud builds list \
    --project="${PROJECT_ID}" \
    --region="${location}" \
    --sort-by='~createTime' \
    --limit=1 \
    --format='value(id)' 2>/dev/null || true)"

  if [[ -z "${build_id}" ]]; then
    note "No readable build found in ${location}."
    return 0
  fi

  gcloud builds describe "${build_id}" \
    --project="${PROJECT_ID}" \
    --region="${location}" \
    --format='yaml(id,status,createTime,finishTime,serviceAccount,logUrl,results.images)' \
    || true

  note "--- build log: ${build_id} ---"
  gcloud builds log "${build_id}" \
    --project="${PROJECT_ID}" \
    --region="${location}" \
    || note "Build log could not be read with the active account."
  note "--- end build log ---"
}

capture_run_diagnostics() {
  section "Cloud Run diagnostics"
  gcloud run services describe "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format='yaml(metadata.name,status.url,status.latestCreatedRevisionName,status.latestReadyRevisionName,status.conditions)' \
    || note "No readable Cloud Run service exists yet."

  gcloud logging read \
    "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${SERVICE_NAME}\"" \
    --project="${PROJECT_ID}" \
    --freshness=2h \
    --limit=40 \
    --format='table(timestamp,severity,textPayload,jsonPayload.message)' \
    || note "Recent revision logs could not be read."
}

finalize_report() {
  local code="$?"
  set +e
  if [[ "${code}" -ne 0 ]]; then
    section "Automatic diagnostics after failure"
    capture_build "${REGION}" "After failure"
    capture_run_diagnostics
    note "FINAL_STATUS=FAILED"
    note "EXIT_CODE=${code}"
  fi
  cp "${REPORT}" "${LATEST_REPORT}"
  note "REPORT=${LATEST_REPORT}"
  return "${code}"
}
trap finalize_report EXIT

section "Preflight"
require_command gcloud
require_command python3

if [[ ! "${PROJECT_ID}" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]]; then
  die "Invalid Google Cloud project ID: ${PROJECT_ID}" 2
fi

ACTIVE_ACCOUNT="$(gcloud auth list \
  --filter='status:ACTIVE' \
  --limit=1 \
  --format='value(account)')"
[[ -n "${ACTIVE_ACCOUNT}" ]] || die "Cloud Shell has no active Google account." 2

gcloud projects describe "${PROJECT_ID}" --format='value(projectId)' >/dev/null \
  || die "The active account cannot access ${PROJECT_ID}." 2
gcloud config set project "${PROJECT_ID}" >/dev/null
gcloud config set run/region "${REGION}" >/dev/null
gcloud config set builds/region "${REGION}" >/dev/null

PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
[[ -n "${PROJECT_NUMBER}" ]] || die "Could not determine the project number." 2

note "Project: ${PROJECT_ID} (${PROJECT_NUMBER})"
note "Account: ${ACTIVE_ACCOUNT}"
note "Region: ${REGION}"

# Diagnose the failed attempt before changing anything.
capture_build "${REGION}" "Before recovery"

section "Billing safety gate"
BILLING_ENABLED="$(gcloud billing projects describe "${PROJECT_ID}" \
  --format='value(billingEnabled)' 2>/dev/null || true)"
case "${BILLING_ENABLED}" in
  True|true)
    note "Billing is enabled. Continuing within the deployment limits in this script."
    ;;
  False|false)
    die "Billing is disabled. The script will not attach or choose a billing account automatically." 3
    ;;
  *)
    die "Billing status could not be verified. No billable resources were changed." 3
    ;;
esac

section "Required APIs"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  iam.googleapis.com \
  logging.googleapis.com \
  compute.googleapis.com \
  --project="${PROJECT_ID}" \
  --quiet

BUILD_ACCOUNT_NAME="places-again-builder"
BUILD_SERVICE_ACCOUNT="${BUILD_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_SERVICE_ACCOUNT_RESOURCE="projects/${PROJECT_ID}/serviceAccounts/${BUILD_SERVICE_ACCOUNT}"
RUNTIME_ACCOUNT_NAME="places-again-runtime"
RUNTIME_SERVICE_ACCOUNT="${RUNTIME_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if [[ "${ACTIVE_ACCOUNT}" == *.gserviceaccount.com ]]; then
  ACTIVE_MEMBER="serviceAccount:${ACTIVE_ACCOUNT}"
else
  ACTIVE_MEMBER="user:${ACTIVE_ACCOUNT}"
fi

ensure_service_account() {
  local name="$1"
  local email="$2"
  local display_name="$3"
  local description="$4"

  if ! gcloud iam service-accounts describe "${email}" \
    --project="${PROJECT_ID}" >/dev/null 2>&1; then
    gcloud iam service-accounts create "${name}" \
      --project="${PROJECT_ID}" \
      --display-name="${display_name}" \
      --description="${description}" \
      --quiet
  fi
}

grant_project_role() {
  local member="$1"
  local role="$2"
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="${member}" \
    --role="${role}" \
    --condition=None \
    --quiet >/dev/null
}

grant_act_as() {
  local service_account="$1"
  gcloud iam service-accounts add-iam-policy-binding "${service_account}" \
    --project="${PROJECT_ID}" \
    --member="${ACTIVE_MEMBER}" \
    --role='roles/iam.serviceAccountUser' \
    --quiet >/dev/null
}

section "Build identity recovery"
ensure_service_account \
  "${BUILD_ACCOUNT_NAME}" \
  "${BUILD_SERVICE_ACCOUNT}" \
  "Places Again source builder" \
  "Dedicated least-privilege Cloud Build identity for Places, Again"
grant_project_role "serviceAccount:${BUILD_SERVICE_ACCOUNT}" 'roles/run.builder'
grant_act_as "${BUILD_SERVICE_ACCOUNT}"
note "Build identity fixed explicitly: ${BUILD_SERVICE_ACCOUNT}"

section "Runtime identity"
ensure_service_account \
  "${RUNTIME_ACCOUNT_NAME}" \
  "${RUNTIME_SERVICE_ACCOUNT}" \
  "Places Again Cloud Run runtime" \
  "Least-privilege runtime identity for Places, Again"
grant_project_role "serviceAccount:${RUNTIME_SERVICE_ACCOUNT}" 'roles/datastore.user'
grant_project_role "serviceAccount:${RUNTIME_SERVICE_ACCOUNT}" 'roles/aiplatform.user'
grant_act_as "${RUNTIME_SERVICE_ACCOUNT}"
note "Runtime identity ready: ${RUNTIME_SERVICE_ACCOUNT}"

section "Firestore"
if gcloud firestore databases describe \
  --database='(default)' \
  --project="${PROJECT_ID}" >/dev/null 2>&1; then
  DATABASE_LOCATION="$(gcloud firestore databases describe \
    --database='(default)' \
    --project="${PROJECT_ID}" \
    --format='value(locationId)' 2>/dev/null || true)"
  note "Firestore already exists${DATABASE_LOCATION:+ in ${DATABASE_LOCATION}}."
else
  gcloud firestore databases create \
    --database='(default)' \
    --project="${PROJECT_ID}" \
    --location="${FIRESTORE_LOCATION}" \
    --edition=standard \
    --type=firestore-native \
    --quiet
  note "Firestore created in ${FIRESTORE_LOCATION}."
fi

deploy_once() {
  local attempt="$1"
  section "Cloud Run deployment — attempt ${attempt}/2"
  : > "${DEPLOY_OUTPUT}"
  gcloud run deploy "${SERVICE_NAME}" \
    --source="${SCRIPT_DIR}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --build-service-account="${BUILD_SERVICE_ACCOUNT_RESOURCE}" \
    --service-account="${RUNTIME_SERVICE_ACCOUNT}" \
    --allow-unauthenticated \
    --ingress=all \
    --min-instances=0 \
    --max-instances=1 \
    --memory=512Mi \
    --cpu=1 \
    --concurrency=1 \
    --timeout=300 \
    --set-env-vars="PLACES_AGAIN_MODEL=${MODEL},PLACES_AGAIN_REPOSITORY=firestore,PLACES_AGAIN_AGENT_RUNS_PER_HOUR=12,GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global" \
    --quiet 2>&1 | tee "${DEPLOY_OUTPUT}"
}

if ! deploy_once 1; then
  section "Bounded automatic recovery"
  capture_build "${REGION}" "Failed deployment"
  note "Reapplying the dedicated builder role and waiting once for IAM propagation."
  grant_project_role "serviceAccount:${BUILD_SERVICE_ACCOUNT}" 'roles/run.builder'
  sleep 25
  deploy_once 2 || die "Deployment failed after one automatic retry." 7
fi

section "Public verification"
SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format='value(status.url)')"
[[ "${SERVICE_URL}" == https://* ]] || die "Cloud Run did not return a service URL." 8

python3 "${SCRIPT_DIR}/scripts/smoke_test.py" "${SERVICE_URL}"

capture_build "${REGION}" "Successful deployment"
section "Result"
note "FINAL_STATUS=SUCCESS"
note "SERVICE_URL=${SERVICE_URL}"
note "The Cloud Run, Vertex AI, Firestore, and unsent-outbox checks all passed."
