#!/usr/bin/env bash

# Apply the dedicated runtime identity, then prove the deployed service works.

set -Eeuo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Cloud Run Button did not provide GOOGLE_CLOUD_PROJECT}"
REGION="${GOOGLE_CLOUD_REGION:-europe-west1}"
SERVICE="${K_SERVICE:-places-again}"
SERVICE_URL="${SERVICE_URL:-}"
RUNTIME_SERVICE_ACCOUNT="places-again-runtime@${PROJECT_ID}.iam.gserviceaccount.com"

note() { printf '[Places, Again] %s\n' "$*"; }

note "Applying the dedicated runtime identity and bounded demo settings."
gcloud run services update "${SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --service-account="${RUNTIME_SERVICE_ACCOUNT}" \
  --min-instances=0 \
  --max-instances=1 \
  --concurrency=1 \
  --memory=512Mi \
  --cpu=1 \
  --set-env-vars="PLACES_AGAIN_MODEL=gemini-3.5-flash,PLACES_AGAIN_REPOSITORY=firestore,PLACES_AGAIN_AGENT_RUNS_PER_HOUR=12,GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global" \
  --quiet

if [[ -z "${SERVICE_URL}" ]]; then
  SERVICE_URL="$(gcloud run services describe "${SERVICE}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format='value(status.url)')"
fi

[[ "${SERVICE_URL}" == https://* ]] || {
  note "Cloud Run did not return a public service URL."
  exit 8
}

note "Running the complete health and workflow smoke test."
python3 scripts/smoke_test.py "${SERVICE_URL}"
note "Deployment verified: ${SERVICE_URL}"
