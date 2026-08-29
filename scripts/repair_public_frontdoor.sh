#!/usr/bin/env bash

# Repair only the public Cloud Run service front door.
# This does not rebuild the image, redeploy application code, touch the private
# worker, mutate Firestore, or change the Gemini/ADK workflow.

set -Eeuo pipefail

readonly DEFAULT_PROJECT_ID="project-2ee12060-728f-434f-9ad"
readonly REGION="europe-west1"
readonly SERVICE="places-again"
PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT:-${DEFAULT_PROJECT_ID}}}"

note() { printf '[Places, Again][public-frontdoor] %s\n' "$*"; }
die() { note "STOP: $1"; exit "${2:-1}"; }

command -v gcloud >/dev/null 2>&1 || die "gcloud is required." 2
command -v curl >/dev/null 2>&1 || die "curl is required." 2

ACTIVE_ACCOUNT="$(gcloud auth list --filter='status:ACTIVE' --limit=1 --format='value(account)')"
[[ -n "${ACTIVE_ACCOUNT}" ]] || die "No active Google account is available." 2

gcloud projects describe "${PROJECT_ID}" --format='value(projectId)' >/dev/null \
  || die "The active account cannot access ${PROJECT_ID}." 2

gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" >/dev/null \
  || die "Cloud Run service ${SERVICE} was not found in ${PROJECT_ID}/${REGION}." 2

note "project=${PROJECT_ID} account=${ACTIVE_ACCOUNT} service=${SERVICE} region=${REGION}"

BEFORE_DEFAULT_DISABLED="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='value(metadata.annotations."run.googleapis.com/default-url-disabled")' 2>/dev/null || true)"
BEFORE_INGRESS="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='value(metadata.annotations."run.googleapis.com/ingress")' 2>/dev/null || true)"
BEFORE_INVOKER_DISABLED="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='value(metadata.annotations."run.googleapis.com/invoker-iam-disabled")' 2>/dev/null || true)"
note "before ingress=${BEFORE_INGRESS:-unset} default_url_disabled=${BEFORE_DEFAULT_DISABLED:-unset} invoker_iam_disabled=${BEFORE_INVOKER_DISABLED:-unset}"

# Restore every Cloud Run front-door setting required for a public contest demo.
# Google Cloud currently recommends disabling the Invoker IAM check for a public
# service; this also works in projects where domain-restricted sharing makes the
# allUsers binding path fragile.
gcloud run services update "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --ingress=all \
  --default-url \
  --no-invoker-iam-check \
  --quiet >/dev/null

# Keep the classic binding too when the project permits it. Failure here is not
# fatal because --no-invoker-iam-check is the authoritative public-access mode.
set +e
gcloud run services add-iam-policy-binding "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --member='allUsers' \
  --role='roles/run.invoker' \
  --quiet >/dev/null 2>&1
ALLUSERS_EXIT=$?
set -e

API_URL="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')"
INGRESS="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='value(metadata.annotations."run.googleapis.com/ingress")')"
DEFAULT_DISABLED="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='value(metadata.annotations."run.googleapis.com/default-url-disabled")' 2>/dev/null || true)"
INVOKER_DISABLED="$(gcloud run services describe "${SERVICE}" \
  --project="${PROJECT_ID}" --region="${REGION}" \
  --format='value(metadata.annotations."run.googleapis.com/invoker-iam-disabled")' 2>/dev/null || true)"

[[ "${INGRESS}" == "all" ]] || die "Ingress is not all: ${INGRESS}" 9
if [[ "${DEFAULT_DISABLED,,}" == "true" ]]; then
  die "Default run.app URL is still disabled." 9
fi
if [[ "${INVOKER_DISABLED,,}" != "true" ]]; then
  die "Cloud Run Invoker IAM check is still enabled; public access is not proven." 9
fi
[[ "${API_URL}" == https://* ]] || die "Cloud Run did not return a default URL." 9

note "after ingress=${INGRESS} default_url_disabled=${DEFAULT_DISABLED:-false} invoker_iam_disabled=${INVOKER_DISABLED} allUsers_binding_exit=${ALLUSERS_EXIT}"
note "API_URL=${API_URL}"

# This request confirms the route from the owner Google environment. The
# independent GitHub Actions probe remains the authoritative public-internet test.
HTTP_CODE="$(curl --silent --show-error --location --output /tmp/places-again-capabilities.json \
  --write-out '%{http_code}' --max-time 30 "${API_URL}/api/capabilities" || true)"
note "owner_environment_capabilities_http=${HTTP_CODE}"
if [[ "${HTTP_CODE}" == "200" ]]; then
  python3 -m json.tool /tmp/places-again-capabilities.json >/dev/null \
    || die "Capabilities endpoint did not return valid JSON." 9
fi

note "FINAL_STATUS=PUBLIC_FRONTDOOR_PUBLIC_MODE_SET"
note "Next proof: rerun the independent GitHub Live Cloud E2E workflow."
