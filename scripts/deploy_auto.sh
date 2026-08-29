#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
KNOWN_PROJECT_ID="project-2ee12060-728f-434f-9ad"

note() { printf '[Places, Again][project-select] %s\n' "$*"; }

ACTIVE_ACCOUNT="$(gcloud auth list --filter='status:ACTIVE' --limit=1 --format='value(account)' 2>/dev/null || true)"
[[ -n "${ACTIVE_ACCOUNT}" ]] || { note "No active Google account is available."; exit 2; }
note "account=${ACTIVE_ACCOUNT}"

mapfile -t ACCESSIBLE_PROJECTS < <(
  gcloud projects list --filter='lifecycleState=ACTIVE' --format='value(projectId)' 2>/dev/null | sed '/^$/d'
)
(( ${#ACCESSIBLE_PROJECTS[@]} > 0 )) || { note "No accessible ACTIVE Google Cloud project was found."; exit 3; }

ELIGIBLE=()
for project_id in "${ACCESSIBLE_PROJECTS[@]}"; do
  if ! gcloud projects describe "${project_id}" --format='value(projectId)' >/dev/null 2>&1; then
    continue
  fi
  billing_enabled="$(gcloud billing projects describe "${project_id}" --format='value(billingEnabled)' 2>/dev/null || true)"
  if [[ "${billing_enabled,,}" == "true" ]]; then
    ELIGIBLE+=("${project_id}")
    note "project=${project_id} access=ok billing=enabled"
  else
    note "project=${project_id} access=ok billing=not_enabled_or_unverifiable action=skip"
  fi
done

(( ${#ELIGIBLE[@]} > 0 )) || {
  note "No accessible project with verifiably enabled billing was found. No deployment attempted."
  exit 4
}

contains_project() {
  local needle="$1" item
  [[ -n "${needle}" ]] || return 1
  for item in "${ELIGIBLE[@]}"; do
    [[ "${item}" == "${needle}" ]] && return 0
  done
  return 1
}

SELECTED=""
CURRENT_PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
CURRENT_PROJECT="${CURRENT_PROJECT#\(unset\)}"

if contains_project "${CURRENT_PROJECT}"; then
  SELECTED="${CURRENT_PROJECT}"
  note "selection=current_config project=${SELECTED}"
elif contains_project "${KNOWN_PROJECT_ID}"; then
  SELECTED="${KNOWN_PROJECT_ID}"
  note "selection=known_places_again_project project=${SELECTED}"
else
  MATCHES=()
  for project_id in "${ELIGIBLE[@]}"; do
    project_name="$(gcloud projects describe "${project_id}" --format='value(name)' 2>/dev/null || true)"
    if [[ "${project_id,,}" == *places*again* || "${project_name,,}" == *places*again* ]]; then
      MATCHES+=("${project_id}")
    fi
  done
  if (( ${#MATCHES[@]} == 1 )); then
    SELECTED="${MATCHES[0]}"
    note "selection=unique_places_again_match project=${SELECTED}"
  elif (( ${#ELIGIBLE[@]} == 1 )); then
    SELECTED="${ELIGIBLE[0]}"
    note "selection=only_billing_enabled_project project=${SELECTED}"
  else
    note "Multiple accessible billing-enabled projects remain and none can be selected safely without owner choice."
    printf '[Places, Again][project-select] candidates=%s\n' "${ELIGIBLE[*]}"
    exit 5
  fi
fi

note "selected_project=${SELECTED} action=deploy"
bash "${ROOT_DIR}/deploy.sh" "${SELECTED}"

# The hosted/default URL state is a service-level property that can persist from
# an older Cloud Run service. Re-assert the judge-facing public front door after
# the authoritative deployment without rebuilding the verified application image.
note "selected_project=${SELECTED} action=verify_public_frontdoor"
bash "${ROOT_DIR}/scripts/repair_public_frontdoor.sh" "${SELECTED}"
