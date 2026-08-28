#!/usr/bin/env bash

# Minimal preparation for Google's guided Cloud Run button. The post-create hook
# delegates the authoritative two-service setup and E2E proof to deploy.sh.

set -Eeuo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Cloud Run Button did not provide GOOGLE_CLOUD_PROJECT}"

note() { printf '[Places, Again] %s\n' "$*"; }

note "Checking billing before any deployable resource is changed."
BILLING_ENABLED="$(gcloud billing projects describe "${PROJECT_ID}" --format='value(billingEnabled)' 2>/dev/null || true)"
[[ "${BILLING_ENABLED,,}" == "true" ]] || {
  note "Billing is not enabled. No billing account was attached automatically."
  exit 3
}

note "Enabling APIs required by the guided build and authoritative deployment."
gcloud services enable \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  aiplatform.googleapis.com firestore.googleapis.com pubsub.googleapis.com \
  iam.googleapis.com iamcredentials.googleapis.com logging.googleapis.com \
  --project="${PROJECT_ID}" --quiet
