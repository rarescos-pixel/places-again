#!/usr/bin/env bash

# Replace the temporary guided service with the same audited architecture used
# by command-line deployment, then run the real cloud E2E evidence gate.

set -Eeuo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Cloud Run Button did not provide GOOGLE_CLOUD_PROJECT}"
PLACES_AGAIN_PREBUILT_IMAGE="${IMAGE_URL:?Cloud Run Button did not provide IMAGE_URL}" \
  exec bash deploy.sh "${PROJECT_ID}"
