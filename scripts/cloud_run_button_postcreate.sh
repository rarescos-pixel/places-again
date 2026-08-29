#!/usr/bin/env bash

# Replace the temporary guided service with the same audited architecture used
# by command-line deployment, run the real cloud E2E evidence gate, then reassert
# the judge-facing public Cloud Run endpoint.

set -Eeuo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Cloud Run Button did not provide GOOGLE_CLOUD_PROJECT}"
PLACES_AGAIN_PREBUILT_IMAGE="${IMAGE_URL:?Cloud Run Button did not provide IMAGE_URL}" \
  bash deploy.sh "${PROJECT_ID}"

bash scripts/repair_public_frontdoor.sh "${PROJECT_ID}"
