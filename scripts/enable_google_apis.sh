#!/usr/bin/env bash

# Enable Google Cloud APIs without turning Service Usage rate limits into a
# fragile all-or-nothing deployment step. This file is sourced by both the
# guided Cloud Run build and the authoritative deployment.

set -Eeuo pipefail

api_enable_log() {
  printf '[Places, Again][api-enable] %s\n' "$*"
}

api_enable_is_transient() {
  local message="$1"
  grep -Eiq \
    '(^|[^0-9])429([^0-9]|$)|RESOURCE_EXHAUSTED|rate.?limit|quota exceeded|UNAVAILABLE|DEADLINE_EXCEEDED|INTERNAL|backend error|temporar|connection reset|connection refused|HTTP[[:space:]]+5[0-9][0-9]' \
    <<<"${message}"
}

api_enable_retry_delay() {
  local attempt="$1"
  local base_seconds="${PLACES_AGAIN_API_RETRY_BASE_SECONDS:-4}"
  local cap_seconds="${PLACES_AGAIN_API_RETRY_CAP_SECONDS:-45}"
  local jitter_seconds="${PLACES_AGAIN_API_RETRY_JITTER_SECONDS:-3}"
  local delay=$((base_seconds * (2 ** (attempt - 1))))
  local jitter=0

  if (( delay > cap_seconds )); then
    delay="${cap_seconds}"
  fi
  if (( jitter_seconds > 0 )); then
    jitter=$((RANDOM % (jitter_seconds + 1)))
  fi
  printf '%s' "$((delay + jitter))"
}

# The most recent command output is deliberately kept in a global so callers
# can inspect a successful `services list` without command-substitution hiding
# the logging and retry state in a subshell.
API_ENABLE_COMMAND_OUTPUT=""

api_enable_run_with_retry() {
  local label="$1"
  shift
  local max_attempts="${PLACES_AGAIN_API_RETRY_MAX_ATTEMPTS:-6}"
  local attempt exit_code delay

  API_ENABLE_COMMAND_OUTPUT=""
  for ((attempt = 1; attempt <= max_attempts; attempt += 1)); do
    if API_ENABLE_COMMAND_OUTPUT="$("$@" 2>&1)"; then
      api_enable_log "operation=${label} attempt=${attempt} result=success"
      return 0
    else
      exit_code="$?"
    fi

    if ! api_enable_is_transient "${API_ENABLE_COMMAND_OUTPUT}"; then
      api_enable_log "operation=${label} attempt=${attempt} result=failed retryable=false exit_code=${exit_code}"
      printf '%s\n' "${API_ENABLE_COMMAND_OUTPUT}" >&2
      return "${exit_code}"
    fi

    if (( attempt == max_attempts )); then
      api_enable_log "operation=${label} attempt=${attempt} result=failed retryable=true exhausted=true exit_code=${exit_code}"
      printf '%s\n' "${API_ENABLE_COMMAND_OUTPUT}" >&2
      return "${exit_code}"
    fi

    delay="$(api_enable_retry_delay "${attempt}")"
    api_enable_log "operation=${label} attempt=${attempt} result=retry retryable=true delay_seconds=${delay} exit_code=${exit_code}"
    printf '%s\n' "${API_ENABLE_COMMAND_OUTPUT}" >&2
    sleep "${delay}"
  done
}

enable_google_apis() {
  local project_id="$1"
  shift
  local -a required_apis=("$@")
  local enabled_apis api
  local pacing_seconds="${PLACES_AGAIN_API_ENABLE_PACING_SECONDS:-2}"

  [[ -n "${project_id}" ]] || {
    api_enable_log "result=failed reason=missing_project_id"
    return 2
  }
  (( ${#required_apis[@]} > 0 )) || {
    api_enable_log "result=success required=0 enabled=0"
    return 0
  }

  api_enable_log "project=${project_id} required=${#required_apis[@]} strategy=check_then_enable_individually"
  api_enable_run_with_retry "list-enabled" \
    gcloud services list --enabled --project="${project_id}" --format='value(config.name)'
  enabled_apis="${API_ENABLE_COMMAND_OUTPUT}"

  for api in "${required_apis[@]}"; do
    if grep -Fxq -- "${api}" <<<"${enabled_apis}"; then
      api_enable_log "api=${api} state=already_enabled action=skip"
      continue
    fi

    api_enable_log "api=${api} state=missing action=enable"
    api_enable_run_with_retry "enable:${api}" \
      gcloud services enable "${api}" --project="${project_id}" --quiet
    api_enable_log "api=${api} state=enabled action=complete"

    # Pace mutations even after a successful request. Service Usage has a low
    # per-minute mutation quota on fresh projects.
    if (( pacing_seconds > 0 )); then
      sleep "${pacing_seconds}"
    fi
  done

  api_enable_log "project=${project_id} result=success"
}
