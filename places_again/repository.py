from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Callable, TypeVar


ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = ROOT / "data" / "demo_state.json"
MutationResult = TypeVar("MutationResult")


class JsonRepository:
    def __init__(self, path: Path | None = None):
        configured = os.environ.get("PLACES_AGAIN_STATE_PATH")
        self.path = path or (Path(configured) if configured else ROOT / "runtime" / "state.json")
        self._lock = RLock()

    def reset(self) -> dict[str, Any]:
        state = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        self.save(state)
        return state

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return self.reset()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.load())

    def mutate(
        self,
        mutation: Callable[[dict[str, Any]], tuple[dict[str, Any], MutationResult]],
    ) -> MutationResult:
        """Apply one state transition under a process-local lock."""
        with self._lock:
            state = self.load()
            updated, result = mutation(deepcopy(state))
            self.save(updated)
            return result


class FirestoreRepository:
    """Cloud Run repository using Application Default Credentials."""

    def __init__(self, client: Any | None = None):
        if client is None:
            from google.cloud import firestore

            client = firestore.Client()
        self.client = client
        collection = os.environ.get("PLACES_AGAIN_FIRESTORE_COLLECTION", "places_again")
        document = os.environ.get("PLACES_AGAIN_PRODUCTION_ID", "demo-production")
        self.document = client.collection(collection).document(document)

    def reset(self) -> dict[str, Any]:
        state = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        self.save(state)
        return state

    def load(self) -> dict[str, Any]:
        snapshot = self.document.get()
        if not snapshot.exists:
            return self.reset()
        payload = snapshot.to_dict() or {}
        return payload["state"]

    def save(self, state: dict[str, Any]) -> None:
        self.document.set({"state": deepcopy(state)})

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.load())

    def mutate(
        self,
        mutation: Callable[[dict[str, Any]], tuple[dict[str, Any], MutationResult]],
    ) -> MutationResult:
        """Apply one state transition atomically in Firestore.

        Firestore may retry the callback after a concurrent write, so callers
        must keep mutation callbacks deterministic apart from values already
        captured before this method is invoked.
        """
        from google.cloud import firestore

        transaction = self.client.transaction()

        @firestore.transactional
        def apply_in_transaction(active_transaction):
            snapshot = self.document.get(transaction=active_transaction)
            if snapshot.exists:
                payload = snapshot.to_dict() or {}
                state = payload["state"]
            else:
                state = json.loads(SEED_PATH.read_text(encoding="utf-8"))
            updated, result = mutation(deepcopy(state))
            active_transaction.set(self.document, {"state": deepcopy(updated)})
            return result

        return apply_in_transaction(transaction)


def create_repository() -> JsonRepository | FirestoreRepository:
    mode = os.environ.get("PLACES_AGAIN_REPOSITORY", "json").lower()
    if mode == "firestore":
        return FirestoreRepository()
    if mode != "json":
        raise ValueError("PLACES_AGAIN_REPOSITORY must be json or firestore")
    return JsonRepository()


repository = create_repository()
