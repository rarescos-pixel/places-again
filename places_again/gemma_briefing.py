from __future__ import annotations

import json
import os
from typing import Any

import google.auth
from google.auth.transport.requests import AuthorizedSession


GEMMA_MODEL = "gemma-4-26b-a4b-it-maas"
GEMMA_LOCATION = "global"
CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
TERMINAL_STATUSES = {"completed", "human_required"}
METRIC_KEYS = (
    "affected_activities",
    "affected_people",
    "affected_resources",
    "person_hours_at_risk",
    "recovered_activities",
    "person_hours_restored",
    "unaffected_activities_moved",
    "unresolved_activities",
    "shifted_minutes",
    "people_schedule_changed",
    "resources_rescheduled",
    "highest_priority_activities_moved",
    "maximum_cover_minutes",
)


def audited_briefing_input(event: dict[str, Any]) -> dict[str, Any]:
    """Return only bounded, observable event facts for an advisory briefing.

    Free-form incident text, hidden model reasoning, tool traces, and raw plan
    internals are intentionally excluded. Gemma receives facts that are already
    present in the immutable/terminal recovery record; it has no authority over
    recovery selection, verification, commit, or delivery.
    """
    if not isinstance(event, dict):
        raise ValueError("event must be an object")
    status = event.get("status")
    if status not in TERMINAL_STATUSES:
        raise ValueError("Gemma briefing is available only for terminal events")

    metrics = event.get("metrics") if isinstance(event.get("metrics"), dict) else {}
    bounded_metrics = {
        key: metrics[key]
        for key in METRIC_KEYS
        if key in metrics and isinstance(metrics[key], (int, float))
    }
    verification = event.get("deterministic_reverification")
    if not isinstance(verification, dict):
        verification = event.get("verification")
    verification_passed = (
        verification.get("passed") if isinstance(verification, dict) else None
    )

    reason_codes = event.get("selection_reason_codes")
    if not isinstance(reason_codes, list):
        reason_codes = []
    rationale = event.get("selection_rationale")
    if not isinstance(rationale, list):
        rationale = []

    return {
        "event_id": event.get("event_id"),
        "scenario_id": event.get("scenario_id"),
        "status": status,
        "outcome": event.get("outcome"),
        "safe_candidates_considered": event.get("safe_candidates_considered"),
        "selected_candidate_id": event.get("selected_candidate_id"),
        "selection_reason_codes": [str(value)[:80] for value in reason_codes[:2]],
        "selection_rationale": [str(value)[:160] for value in rationale[:2]],
        "base_version": event.get("base_version"),
        "final_version": event.get("final_version"),
        "metrics": bounded_metrics,
        "deterministic_reverification_passed": verification_passed,
        "outbox_status": event.get("outbox_status"),
        "outbox_count": event.get("outbox_count"),
        "messages_sent": event.get("messages_sent", 0),
    }


def briefing_prompt(summary: dict[str, Any]) -> str:
    compact = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    return (
        "Create a concise manager handoff from the audited recovery record below. "
        "Use only facts present in the JSON. Do not invent impact, savings, causes, "
        "or recommendations. Do not expose hidden reasoning. In at most 80 words, "
        "write four short labeled lines: Outcome, Choice, Safety, Handoff. "
        "If the event is human_required, say that no autonomous recovery was committed.\n\n"
        f"AUDITED_RECOVERY_RECORD={compact}"
    )


def gemma_endpoint(project_id: str) -> str:
    project_id = project_id.strip()
    if not project_id:
        raise ValueError("Google Cloud project ID is required")
    return (
        "https://aiplatform.googleapis.com/v1/projects/"
        f"{project_id}/locations/{GEMMA_LOCATION}/endpoints/openapi/chat/completions"
    )


def generate_gemma_briefing(
    event: dict[str, Any],
    *,
    project_id: str | None = None,
    session: Any | None = None,
    timeout_seconds: int = 90,
) -> dict[str, Any]:
    """Generate an advisory post-recovery briefing with managed Gemma 4.

    This call is deliberately outside the authority path. It consumes a terminal
    audited event and returns text only. Its result is never used to select or
    commit a recovery plan.
    """
    summary = audited_briefing_input(event)
    resolved_project = (project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or "").strip()

    if session is None:
        credentials, default_project = google.auth.default(scopes=[CLOUD_PLATFORM_SCOPE])
        if not resolved_project:
            resolved_project = (default_project or "").strip()
        if not resolved_project:
            raise ValueError("Could not resolve GOOGLE_CLOUD_PROJECT")
        session = AuthorizedSession(credentials)

    endpoint = gemma_endpoint(resolved_project)
    request_body = {
        "model": f"google/{GEMMA_MODEL}",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a read-only operational briefing writer. You have no "
                    "authority to change the audited recovery record."
                ),
            },
            {"role": "user", "content": briefing_prompt(summary)},
        ],
        "temperature": 0.1,
        "max_tokens": 220,
    }
    response = session.post(endpoint, json=request_body, timeout=timeout_seconds)
    response.raise_for_status()
    payload = response.json()
    try:
        text = payload["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as error:
        raise ValueError("Gemma response did not contain assistant content") from error
    if not text:
        raise ValueError("Gemma returned an empty briefing")

    return {
        "model": GEMMA_MODEL,
        "provider": "Google managed model API on Vertex AI",
        "authority": "advisory_post_recovery_only",
        "project_id": resolved_project,
        "input": summary,
        "briefing": text,
    }
