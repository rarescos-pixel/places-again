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
