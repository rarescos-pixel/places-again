from places_again.repository import FirestoreRepository


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
