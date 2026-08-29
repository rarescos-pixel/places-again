#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from places_again.gemma_briefing import generate_gemma_briefing


def fetch_json(url: str, timeout_seconds: int = 30) -> dict:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # nosec B310
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not fetch event JSON from {url}: {error}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("Event endpoint did not return a JSON object")
    return payload


def event_from_cloud_e2e(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        event = payload["checks"]["safe_autonomous_recovery"]
    except (KeyError, TypeError) as error:
        raise RuntimeError(
            "Cloud E2E evidence does not contain checks.safe_autonomous_recovery"
        ) from error
    if not isinstance(event, dict):
        raise RuntimeError("safe_autonomous_recovery is not an event object")
    return event


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a read-only manager briefing for a completed Places, Again "
            "event using Google's managed Gemma 4 model."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--event-json", help="Path to a terminal event JSON")
    source.add_argument(
        "--cloud-e2e-evidence",
        help="Path to cloud-e2e-evidence-*.json; uses the verified safe event",
    )
    source.add_argument(
        "--event-id",
        help="Completed event ID; requires --api-url",
    )
    parser.add_argument("--api-url", help="Public Places, Again API base URL")
    parser.add_argument("--project-id", help="Google Cloud project ID; defaults to ADC/env")
    parser.add_argument("--output", help="Optional JSON evidence output path")
    args = parser.parse_args()

    if args.event_id and not args.api_url:
        parser.error("--event-id requires --api-url")
    if args.api_url and not args.event_id:
        parser.error("--api-url is valid only with --event-id")

    if args.cloud_e2e_evidence:
        event = event_from_cloud_e2e(Path(args.cloud_e2e_evidence))
    elif args.event_json:
        event = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
    else:
        base = args.api_url.rstrip("/")
        event = fetch_json(f"{base}/api/events/{args.event_id}")

    result = generate_gemma_briefing(event, project_id=args.project_id)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"EVIDENCE_REPORT={output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
