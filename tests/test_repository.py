import json
from copy import deepcopy

from places_again.repository import FirestoreRepository, seed_system


class FakeSnapshot:
    def __init__(self, payload):
        self.payload = payload
        self.exists = payload is not None

    def to_dict(self):
        return self.payload


class FakeDocument:
    def __init__(self):
        self.payload = None

    def get(self):
        return FakeSnapshot(self.payload)

    def set(self, payload):
        self.payload = payload


class FakeCollection:
    def __init__(self, document):
        self._document = document

    def document(self, _document_id):
        return self._document


class FakeClient:
    def __init__(self):
        self.document = FakeDocument()

    def collection(self, _collection_name):
        return FakeCollection(self.document)


def test_firestore_repository_seeds_and_persists_state():
    client = FakeClient()
    repository = FirestoreRepository(client=client)

    state = repository.load()
    assert state["version"] == 1
    assert client.document.payload["state"]["production"].startswith("La Traviata")

    state["version"] = 7
    repository.save(state)
    state["version"] = 99

    assert repository.load()["version"] == 7


def test_json_repository_mutation_is_persisted(tmp_path):
    from places_again.repository import JsonRepository

    repository = JsonRepository(tmp_path / "state.json")

    def advance(state):
        state["version"] += 1
        return state, state["version"]

    assert repository.mutate(advance) == 2
    assert repository.load()["version"] == 2


def test_firestore_encoding_compacts_terminal_candidate_set_and_agent_trace():
    system = seed_system()
    event_id = "event-proof"
    system["events"][event_id] = {
        "event_id": event_id,
        "scenario_id": "opera",
        "status": "completed",
        "candidate_set": {"candidates": [{"blob": "x" * 250_000}]},
        "candidate_summaries": [
            {"candidate_id": "candidate-a", "metrics": {"shifted_minutes": 270}}
        ],
        "selected_candidate_id": "candidate-a",
        "selection_reason_codes": ["preserve_highest_priority_activity"],
        "deterministic_reverification": {"passed": True, "checks": {"safe": True}},
        "metrics": {"activities_recovered": 3},
        "agent_trace": [
            {
                "type": "tool_call",
                "name": "prepare_recovery_candidates",
                "arguments": {"event_id": event_id},
            },
            {
                "type": "tool_result",
                "name": "prepare_recovery_candidates",
                "result": {
                    "status": "planned",
                    "candidate_set": {"blob": "y" * 250_000},
                    "safe_candidates_considered": 2,
                },
            },
            {
                "type": "tool_result",
                "name": "select_recovery_candidate",
                "result": {
                    "status": "completed",
                    "selected_candidate_id": "candidate-a",
                    "deterministic_reverification": {
                        "passed": True,
                        "checks": {"huge": "z" * 250_000},
                    },
                    "messages_sent": 0,
                },
            },
        ],
    }

    encoded = FirestoreRepository._encode(system)
    persisted = encoded["system"]["events"][event_id]

    assert "candidate_set" not in persisted
    assert persisted["candidate_summaries"] == system["events"][event_id]["candidate_summaries"]
    assert persisted["selected_candidate_id"] == "candidate-a"
    assert persisted["agent_trace"][0]["name"] == "prepare_recovery_candidates"
    assert persisted["agent_trace"][1]["result"] == {
        "status": "planned",
        "safe_candidates_considered": 2,
    }
    assert persisted["agent_trace"][2]["result"] == {
        "status": "completed",
        "selected_candidate_id": "candidate-a",
        "messages_sent": 0,
        "deterministic_reverification": {"passed": True},
    }


def test_firestore_encoding_stays_bounded_under_repeated_terminal_demo_evidence():
    system = seed_system()
    template = {
        "scenario_id": "opera",
        "status": "completed",
        "candidate_set": {"candidates": [{"blob": "x" * 80_000}]},
        "candidate_summaries": [
            {"candidate_id": "candidate-a", "metrics": {"shifted_minutes": 270}},
            {"candidate_id": "candidate-b", "metrics": {"shifted_minutes": 240}},
        ],
        "selected_candidate_id": "candidate-a",
        "selection_reason_codes": ["preserve_highest_priority_activity"],
        "deterministic_reverification": {"passed": True},
        "metrics": {"activities_recovered": 3, "person_hours_restored": 12},
        "agent_trace": [
            {
                "type": "tool_result",
                "name": "get_event_status",
                "result": {"status": "completed", "payload": "y" * 80_000},
            }
        ],
    }
    for index in range(40):
        event = deepcopy(template)
        event["event_id"] = f"event-{index}"
        system["events"][event["event_id"]] = event

    encoded = FirestoreRepository._encode(system)
    encoded_bytes = len(json.dumps(encoded, separators=(",", ":")).encode("utf-8"))

    assert encoded_bytes < 400_000
    assert all(
        "candidate_set" not in event
        for event in encoded["system"]["events"].values()
    )
