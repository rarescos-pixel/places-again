import base64
import json

from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest

from places_again.repository import JsonRepository
import places_again.repository as repository_module
import places_again.tools as tools_module
import places_again.web as web_module


def test_finalist_ui_exposes_taskmaster_proof_points():
    client = TestClient(web_module.app)
    response = client.get("/")
    assert response.status_code == 200
    page = response.text
    assert "The plan breaks." in page
    assert "Commercial Film / Broadcast Production" in page
    assert "Operational Blast Radius" in page
    assert "Incident cascade" in page
    assert "Bounded Gemini decision" in page
    assert "Deterministic re-verification" in page
    assert "Pub/Sub" in page
    assert "prepared not sent" in page.lower()


def test_demo_runs_end_to_end(tmp_path, monkeypatch):
    test_repository = JsonRepository(tmp_path / "state.json")
    monkeypatch.setattr(repository_module, "repository", test_repository)
    monkeypatch.setattr(tools_module, "repository", test_repository)
    monkeypatch.setattr(web_module, "repository", test_repository)
    client = TestClient(web_module.app)

    response = client.post("/api/demo/run")
    assert response.status_code == 200
    payload = response.json()
    assert payload["committed"] is True
    assert payload["new_version"] == 2
    assert payload["plan"]["metrics"]["unresolved"] == 0
    assert payload["call_sheets"]


def test_public_arbitrary_agent_prompt_is_not_exposed():
    client = TestClient(web_module.app)
    response = client.post("/api/agent", json={"message": "Recover the schedule"})
    assert response.status_code == 404


def test_pubsub_worker_route_is_unreachable_on_public_api(monkeypatch):
    monkeypatch.setenv("PLACES_AGAIN_SERVICE_ROLE", "api")
    payload = base64.b64encode(
        json.dumps({"event_id": "00000000-0000-0000-0000-000000000000"}).encode()
    ).decode()
    response = TestClient(web_module.app).post(
        "/api/pubsub/push", json={"message": {"data": payload}}
    )
    assert response.status_code == 404


def test_cloud_run_gates_synthetic_reset_and_legacy_mutation_routes(monkeypatch):
    monkeypatch.setenv("K_SERVICE", "places-again")
    monkeypatch.delenv("PLACES_AGAIN_SYNTHETIC_DEMO_MODE", raising=False)
    client = TestClient(web_module.app)

    assert client.post("/api/demo/reset").status_code == 403
    assert client.post("/api/demo/run").status_code == 403
    assert client.post("/api/demo/preview").status_code == 403
    assert client.post(
        "/api/plans/commit", json={"scenario_id": "opera", "plan_id": "plan-12345678"}
    ).status_code == 403
    assert client.post(
        "/api/recover",
        json={
            "scenario_id": "opera",
            "commit": True,
            "disruption": {
                "person_id": "soprano_principal",
                "start": "08:00",
                "end": "14:00",
                "reason": "illness",
            },
        },
    ).status_code == 403
    assert client.post(
        "/api/events/person-unavailable",
        json={
            "reset_demo": True,
            "disruption": {
                "person_id": "soprano_principal",
                "start": "08:00",
                "end": "14:00",
                "reason": "illness",
            },
        },
    ).status_code == 403


def test_worker_acknowledges_poison_push_without_schedule_effect(tmp_path, monkeypatch):
    test_repository = JsonRepository(tmp_path / "state.json")
    monkeypatch.setenv("PLACES_AGAIN_SERVICE_ROLE", "worker")
    monkeypatch.setattr(repository_module, "repository", test_repository)
    monkeypatch.setattr(tools_module, "repository", test_repository)
    monkeypatch.setattr(web_module, "repository", test_repository)
    client = TestClient(web_module.app)

    response = client.post("/api/pubsub/push", json={"message": {"data": "bad"}})

    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "reason": "invalid_payload"}
    assert test_repository.snapshot("opera")["version"] == 1
    assert any(
        entry["event"] == "pubsub_push_ignored"
        for entry in test_repository.system_snapshot()["audit"]
    )


def test_event_endpoint_runs_as_background_workflow_without_local_gemini(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    test_repository = JsonRepository(tmp_path / "state.json")
    monkeypatch.setattr(repository_module, "repository", test_repository)
    monkeypatch.setattr(tools_module, "repository", test_repository)
    monkeypatch.setattr(web_module, "repository", test_repository)
    client = TestClient(web_module.app)
    response = client.post(
        "/api/events/person-unavailable",
        json={
            "disruption": {
                "person_id": "soprano_principal",
                "start": "08:00",
                "end": "14:00",
                "reason": "illness",
            }
        },
    )
    assert response.status_code == 202
    event = client.get(response.json()["status_url"]).json()
    assert event["status"] == "completed"
    assert event["outcome"] == "autonomous_safe_commit"
    assert event["messages_sent"] == 0


def test_vertex_configuration_is_reported(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    client = TestClient(web_module.app)
    payload = client.get("/api/capabilities").json()
    assert payload["gemini_configured"] is True
    assert payload["model_backend"] == "Vertex AI"


def test_capabilities_scope_exactly_once_claim_to_firestore(monkeypatch):
    client = TestClient(web_module.app)
    monkeypatch.setenv("PLACES_AGAIN_REPOSITORY", "json")
    local = client.get("/api/capabilities").json()
    assert local["effect_semantics"] == (
        "single-process idempotent fallback; cloud proof required"
    )

    monkeypatch.setenv("PLACES_AGAIN_REPOSITORY", "firestore")
    cloud = client.get("/api/capabilities").json()
    assert cloud["effect_semantics"] == (
        "exactly-once business effect via Firestore transaction"
    )


def test_public_agent_rate_limit(monkeypatch):
    monkeypatch.setenv("PLACES_AGAIN_AGENT_RUNS_PER_HOUR", "1")
    web_module._agent_run_times.clear()
    web_module._claim_agent_run_slot()

    with pytest.raises(HTTPException) as error:
        web_module._claim_agent_run_slot()

    assert error.value.status_code == 429
    web_module._agent_run_times.clear()


def test_invalid_agent_rate_limit_falls_back(monkeypatch):
    monkeypatch.setenv("PLACES_AGAIN_AGENT_RUNS_PER_HOUR", "not-a-number")
    assert web_module._agent_runs_per_hour() == 12


def test_preview_then_commit_keeps_messages_unsent(tmp_path, monkeypatch):
    test_repository = JsonRepository(tmp_path / "state.json")
    monkeypatch.setattr(repository_module, "repository", test_repository)
    monkeypatch.setattr(tools_module, "repository", test_repository)
    monkeypatch.setattr(web_module, "repository", test_repository)
    client = TestClient(web_module.app)

    preview = client.post("/api/demo/preview").json()
    assert preview["committed"] is False
    assert preview["plan"]["verification"]["passed"] is True
    assert client.get("/api/state").json()["version"] == 1

    committed = client.post("/api/plans/commit", json={"plan_id": preview["plan"]["plan_id"]}).json()
    assert committed["new_version"] == 2
    assert committed["call_sheets"]
    assert all(item["status"] == "prepared_not_sent" for item in committed["call_sheets"])
