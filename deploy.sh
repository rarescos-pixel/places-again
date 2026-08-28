#!/usr/bin/env bash

# Places, Again — one-command Taskmaster deployment.
#
# Creates a public incident API, an IAM-private Pub/Sub worker, Firestore state,
# Vertex AI access, four least-privilege identities, and authenticated OIDC push.
# It then runs safe/replay/impossible E2E workflows and writes an evidence report.

set -Eeuo pipefail

readonly DEFAULT_PROJECT_ID="project-2ee12060-728f-434f-9ad"
readonly API_SERVICE="places-again"
readonly WORKER_SERVICE="places-again-worker"
readonly TOPIC="places-again-events"
readonly SUBSCRIPTION="places-again-worker-push"
readonly REGION="europe-west1"
readonly FIRESTORE_LOCATION="europe-west1"
readonly MODEL="gemini-3.5-flash"

PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT:-${DEFAULT_PROJECT_ID}}}"
PREBUILT_IMAGE="${PLACES_AGAIN_PREBUILT_IMAGE:-}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${SCRIPT_DIR}/runtime"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="${REPORT_DIR}/deployment-report-${TIMESTAMP}.txt"
LATEST_REPORT="${REPORT_DIR}/deployment-report-latest.txt"
EVIDENCE_REPORT="${REPORT_DIR}/cloud-e2e-evidence-${TIMESTAMP}.json"

mkdir -p "${REPORT_DIR}"
touch "${REPORT}"
exec > >(tee -a "${REPORT}") 2>&1

section() { printf '\n== %s ==\n' "$1"; }
note() { printf '%s\n' "$1"; }
die() { note "STOP: $1"; exit "${2:-1}"; }
require_command() { command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1" 2; }

finalize_report() {
  local code="$?"
  set +e
  if [[ "${code}" -ne 0 ]]; then
    section "Failure diagnostics"
    gcloud run services describe "${API_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" \
      --format='yaml(status.url,status.latestReadyRevisionName,status.conditions)' || true
    gcloud run services describe "${WORKER_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" \
      --format='yaml(status.url,status.latestReadyRevisionName,status.conditions)' || true
    gcloud logging read \
      "resource.type=\"cloud_run_revision\" AND (resource.labels.service_name=\"${API_SERVICE}\" OR resource.labels.service_name=\"${WORKER_SERVICE}\")" \
      --project="${PROJECT_ID}" --freshness=2h --limit=50 \
      --format='table(timestamp,severity,resource.labels.service_name,textPayload,jsonPayload.message)' || true
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

ACTIVE_ACCOUNT="$(gcloud auth list --filter='status:ACTIVE' --limit=1 --format='value(account)')"
[[ -n "${ACTIVE_ACCOUNT}" ]] || die "No active Google account is available." 2
gcloud projects describe "${PROJECT_ID}" --format='value(projectId)' >/dev/null \
  || die "The active account cannot access ${PROJECT_ID}." 2
gcloud config set project "${PROJECT_ID}" >/dev/null
gcloud config set run/region "${REGION}" >/dev/null
gcloud config set builds/region "${REGION}" >/dev/null
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"

note "Project: ${PROJECT_ID} (${PROJECT_NUMBER})"
note "Account: ${ACTIVE_ACCOUNT}"
note "Region: ${REGION}"

section "Billing safety gate"
BILLING_ENABLED="$(gcloud billing projects describe "${PROJECT_ID}" --format='value(billingEnabled)' 2>/dev/null || true)"
case "${BILLING_ENABLED}" in
  True|true) note "Billing is enabled." ;;
  False|false) die "Billing is disabled; no billable deployment was attempted." 3 ;;
  *) die "Billing status could not be verified; no billable deployment was attempted." 3 ;;
esac

section "Google Cloud APIs"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  logging.googleapis.com \
  --project="${PROJECT_ID}" --quiet

BUILD_ACCOUNT="places-again-builder"
API_ACCOUNT="places-again-api"
WORKER_ACCOUNT="places-again-worker"
PUSH_ACCOUNT="places-again-push"
BUILD_SA="${BUILD_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"
API_SA="${API_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"
WORKER_SA="${WORKER_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"
PUSH_SA="${PUSH_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_SA_RESOURCE="projects/${PROJECT_ID}/serviceAccounts/${BUILD_SA}"
PUBSUB_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"

if [[ "${ACTIVE_ACCOUNT}" == *.gserviceaccount.com ]]; then
  ACTIVE_MEMBER="serviceAccount:${ACTIVE_ACCOUNT}"
else
  ACTIVE_MEMBER="user:${ACTIVE_ACCOUNT}"
fi

ensure_service_account() {
  local name="$1" email="$2" display="$3" description="$4"
  if ! gcloud iam service-accounts describe "${email}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    gcloud iam service-accounts create "${name}" --project="${PROJECT_ID}" \
      --display-name="${display}" --description="${description}" --quiet
  fi
}

grant_project_role() {
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="$1" --role="$2" --condition=None --quiet >/dev/null
}

grant_act_as() {
  gcloud iam service-accounts add-iam-policy-binding "$1" --project="${PROJECT_ID}" \
    --member="${ACTIVE_MEMBER}" --role='roles/iam.serviceAccountUser' --quiet >/dev/null
}

section "Least-privilege identities"
ensure_service_account "${BUILD_ACCOUNT}" "${BUILD_SA}" "Places Again builder" "Builds the contest image"
ensure_service_account "${API_ACCOUNT}" "${API_SA}" "Places Again public API" "Persists incidents and publishes opaque event IDs"
ensure_service_account "${WORKER_ACCOUNT}" "${WORKER_SA}" "Places Again private worker" "Runs ADK, Gemini, safety kernel, and Firestore transaction"
ensure_service_account "${PUSH_ACCOUNT}" "${PUSH_SA}" "Places Again PubSub push" "OIDC identity allowed to invoke only the private worker"

grant_project_role "serviceAccount:${BUILD_SA}" 'roles/run.builder'
grant_project_role "serviceAccount:${API_SA}" 'roles/datastore.user'
grant_project_role "serviceAccount:${API_SA}" 'roles/pubsub.publisher'
grant_project_role "serviceAccount:${WORKER_SA}" 'roles/datastore.user'
grant_project_role "serviceAccount:${WORKER_SA}" 'roles/aiplatform.user'
grant_act_as "${BUILD_SA}"
grant_act_as "${API_SA}"
grant_act_as "${WORKER_SA}"
grant_act_as "${PUSH_SA}"
gcloud iam service-accounts add-iam-policy-binding "${PUSH_SA}" --project="${PROJECT_ID}" \
  --member="serviceAccount:${PUBSUB_SERVICE_AGENT}" \
  --role='roles/iam.serviceAccountTokenCreator' --quiet >/dev/null

section "Firestore"
if gcloud firestore databases describe --database='(default)' --project="${PROJECT_ID}" >/dev/null 2>&1; then
  note "Firestore already exists."
else
  gcloud firestore databases create --database='(default)' --project="${PROJECT_ID}" \
    --location="${FIRESTORE_LOCATION}" --edition=standard --type=firestore-native --quiet
fi

section "Pub/Sub topic"
gcloud pubsub topics describe "${TOPIC}" --project="${PROJECT_ID}" >/dev/null 2>&1 \
  || gcloud pubsub topics create "${TOPIC}" --project="${PROJECT_ID}" --quiet

section "Public Cloud Run API"
if [[ -n "${PREBUILT_IMAGE}" ]]; then
  [[ "${PREBUILT_IMAGE}" == *"/"* ]] || die "Invalid prebuilt image reference." 2
  API_ARTIFACT_ARGS=(--image="${PREBUILT_IMAGE}")
  note "Reusing the image already built by the guided deployment."
else
  API_ARTIFACT_ARGS=(--source="${SCRIPT_DIR}" --build-service-account="${BUILD_SA_RESOURCE}")
fi
gcloud run deploy "${API_SERVICE}" \
  "${API_ARTIFACT_ARGS[@]}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service-account="${API_SA}" \
  --allow-unauthenticated \
  --ingress=all \
  --min-instances=0 \
  --max-instances=2 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=20 \
  --timeout=60 \
  --set-env-vars="PLACES_AGAIN_SERVICE_ROLE=api,PLACES_AGAIN_REPOSITORY=firestore,PLACES_AGAIN_PUBSUB_TOPIC=${TOPIC},GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --quiet

API_URL="$(gcloud run services describe "${API_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
IMAGE="$(gcloud run services describe "${API_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(spec.template.spec.containers[0].image)')"
[[ "${API_URL}" == https://* ]] || die "Public API has no Cloud Run URL." 8
[[ -n "${IMAGE}" ]] || die "Could not resolve the built container image." 8

section "Private Cloud Run ADK worker"
gcloud run deploy "${WORKER_SERVICE}" \
  --image="${IMAGE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service-account="${WORKER_SA}" \
  --no-allow-unauthenticated \
  --ingress=internal \
  --min-instances=0 \
  --max-instances=2 \
  --memory=1Gi \
  --cpu=1 \
  --concurrency=4 \
  --timeout=300 \
  --set-env-vars="PLACES_AGAIN_SERVICE_ROLE=worker,PLACES_AGAIN_MODEL=${MODEL},PLACES_AGAIN_REPOSITORY=firestore,PLACES_AGAIN_AGENT_RUNS_PER_HOUR=30,GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global" \
  --quiet

WORKER_URL="$(gcloud run services describe "${WORKER_SERVICE}" --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
[[ "${WORKER_URL}" == https://* ]] || die "Private worker has no Cloud Run URL." 8
gcloud run services add-iam-policy-binding "${WORKER_SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --member="serviceAccount:${PUSH_SA}" --role='roles/run.invoker' --quiet >/dev/null

section "Authenticated Pub/Sub push"
PUSH_ENDPOINT="${WORKER_URL}/api/pubsub/push"
if gcloud pubsub subscriptions describe "${SUBSCRIPTION}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud pubsub subscriptions modify-push-config "${SUBSCRIPTION}" \
    --project="${PROJECT_ID}" \
    --push-endpoint="${PUSH_ENDPOINT}" \
    --push-auth-service-account="${PUSH_SA}" \
    --push-auth-token-audience="${WORKER_URL}" \
    --quiet
  gcloud pubsub subscriptions update "${SUBSCRIPTION}" --project="${PROJECT_ID}" \
    --min-retry-delay=10s --max-retry-delay=60s --quiet
else
  gcloud pubsub subscriptions create "${SUBSCRIPTION}" \
    --project="${PROJECT_ID}" \
    --topic="${TOPIC}" \
    --push-endpoint="${PUSH_ENDPOINT}" \
    --push-auth-service-account="${PUSH_SA}" \
    --push-auth-token-audience="${WORKER_URL}" \
    --ack-deadline=300 \
    --min-retry-delay=10s \
    --max-retry-delay=60s \
    --quiet
fi

section "Cloud E2E evidence"
python3 "${SCRIPT_DIR}/scripts/cloud_e2e_test.py" "${API_URL}" --output "${EVIDENCE_REPORT}"

section "Result"
note "FINAL_STATUS=SUCCESS"
note "API_URL=${API_URL}"
note "WORKER_URL=${WORKER_URL}"
note "PUBSUB_TOPIC=${TOPIC}"
note "PUBSUB_SUBSCRIPTION=${SUBSCRIPTION}"
note "EVIDENCE_REPORT=${EVIDENCE_REPORT}"
note "Cloud Run + Pub/Sub OIDC + Vertex AI/ADK + Firestore + replay/failure proof passed."
