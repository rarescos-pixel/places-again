"""Smoke-test a deployed Places, Again service through its public HTTP API."""

from __future__ import annotations

import json
import sys
from urllib.request import Request, urlopen


EVENT = {
    "disruption": {
        "person_id": "soprano_principal",
        "start": "08:00",
        "end": "14:00",
        "reason": "same-day illness",
    },
    "reset_demo": True,
}


def request(base_url: str, path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    method = "POST" if payload is not None else "GET"
    headers = {"content-type": "application/json"} if body else {}
    call = Request(f"{base_url.rstrip('/')}{path}", data=body, headers=headers, method=method)
    with urlopen(call, timeout=120) as response:
        return json.loads(response.read())


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/smoke_test.py https://SERVICE.run.app")
    base_url = sys.argv[1]
    capabilities = request(base_url, "/api/capabilities")
    assert capabilities["runtime"] == "Google Cloud Run"
    assert capabilities["repository"] == "firestore"
    assert capabilities["gemini_configured"] is True

    result = request(base_url, "/api/events/person-unavailable", EVENT)
    assert result["trigger"] == "person_unavailable"
    assert result["trace"], "Gemini returned no visible tool trace"
    state = request(base_url, "/api/state")
    assert state["version"] == 2
    assert len(state.get("outbox", [])) == 12
    assert all(item["status"] == "prepared_not_sent" for item in state["outbox"])
    print("Cloud Run + Vertex AI + Firestore smoke test passed")


if __name__ == "__main__":
    main()
