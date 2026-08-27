#!/usr/bin/env bash

# Idempotent project preparation for Google's Cloud Run Button.

set -Eeuo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Cloud Run Button did not provide GOOGLE_CLOUD_PROJECT}"
REGION="${GOOGLE_CLOUD_REGION:-europe-west1}"
RUNTIME_ACCOUNT_NAME="places-again-runtime"
RUNTIME_SERVICE_ACCOUNT="${RUNTIME_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

note() { printf '[Places, Again] %s\n' "$*"; }

note "Checking billing before changing billable resources."
BILLING_ENABLED="$(gcloud billing projects describe "${PROJECT_ID}" --format='value(billingEnabled)' 2>/dev/null || true)"
[[ "${BILLING_ENABLED,,}" == "true" ]] || {
  note "Billing is not enabled. No billing account was attached automatically."
  exit 3
}

note "Enabling the APIs required by Cloud Run, Vertex AI, and Firestore."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  iam.googleapis.com \
  logging.googleapis.com \
  --project="${PROJECT_ID}" \
  --quiet

if ! gcloud iam service-accounts describe "${RUNTIME_SERVICE_ACCOUNT}" \
  --project="${PROJECT_ID}" >/dev/null 2>&1; then
  note "Creating the least-privilege runtime identity."
  gcloud iam service-accounts create "${RUNTIME_ACCOUNT_NAME}" \
    --project="${PROJECT_ID}" \
    --display-name="Places Again Cloud Run runtime" \
    --description="Runtime identity for the Places, Again contest demo" \
    --quiet
fi

for role in roles/datastore.user roles/aiplatform.user; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUNTIME_SERVICE_ACCOUNT}" \
    --role="${role}" \
    --condition=None \
    --quiet >/dev/null
done

if gcloud firestore databases describe --database='(default)' \
  --project="${PROJECT_ID}" >/dev/null 2>&1; then
  note "Firestore already exists."
else
  note "Creating Firestore in ${REGION}."
  gcloud firestore databases create \
    --database='(default)' \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --edition=standard \
    --type=firestore-native \
    --quiet
fi

note "Project preparation is complete."
