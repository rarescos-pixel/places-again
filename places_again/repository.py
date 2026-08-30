from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Callable, TypeVar


ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = ROOT / "data" / "scenarios"
LEGACY_SEED_PATH = ROOT / "data" / "demo_state.json"
DEFAULT_SCENARIO = "opera"
TERMINAL_EVENT_STATUSES = frozenset({"completed", "human_required"})
MutationResult = TypeVar("MutationResult")


def _scenario_seed(scenario_id: str) -> dict[str, Any]:
    path = SCENARIO_DIR / f"{scenario_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if scenario_id == DEFAULT_SCENARIO:
        return json.loads(LEGACY_SEED_PATH.read_text(encoding="utf-8"))
    raise KeyError(f"Unknown scenario: {scenario_id}")


def seed_system() -> dict[str, Any]:
    scenarios = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(SCENARIO_DIR.glob("*.json"))
    }
    if DEFAULT_SCENARIO not in scenarios:
        scenarios[DEFAULT_SCENARIO] = _scenario_seed(DEFAULT_SCENARIO)
    return {
        "schema_version": 2,
        "scenarios": scenarios,
        "events": {},
        "audit": [
            {
                "event": "system_seeded",
                "source": "synthetic_scenarios",
                "scenario_count": len(scenarios),
            }
        ],
    }


def _normalize_system(payload: dict[str, Any]) -> dict[str, Any]:
    if "scenarios" in payload and "events" in payload:
        return payload
    system = seed_system()
    system["scenarios"][DEFAULT_SCENARIO] = payload
    system["audit"].append(
        {"event": "legacy_state_migrated", "scenario_id": DEFAULT_SCENARIO}
    )
    return system


def _reset_scenario_in_system(
    system: dict[str, Any], scenario_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Reset synthetic schedule data without erasing event evidence.

    Reset is intentionally refused while an event could still be delivered by
    Pub/Sub. Terminal event records remain as the immutable audit/evidence
    ledger even when the synthetic schedule is returned to its seed state.
    """
    if scenario_id not in system["scenarios"]:
        raise KeyError(f"Unknown scenario: {scenario_id}")
    nonterminal = [
        event_id
        for event_id, event in system.get("events", {}).items()
        if event.get("scenario_id") == scenario_id
        and event.get("status") not in TERMINAL_EVENT_STATUSES
    ]
    if nonterminal:
        raise ValueError(
            "Cannot reset a scenario while events are still processing: "
            + ", ".join(sorted(nonterminal))
        )
    state = _scenario_seed(scenario_id)
    system["scenarios"][scenario_id] = state
    system.setdefault("audit", []).append(
        {
            "event": "synthetic_scenario_reset",
            "scenario_id": scenario_id,
            "preserved_terminal_events": sum(
                1
                for event in system.get("events", {}).values()
                if event.get("scenario_id") == scenario_id
                and event.get("status") in TERMINAL_EVENT_STATUSES
            ),
        }
    )
    return system, deepcopy(state)


class JsonRepository:
    def __init__(self, path: Path | None = None):
        configured = os.environ.get("PLACES_AGAIN_STATE_PATH")
        self.path = path or (
            Path(configured) if configured else ROOT / "runtime" / "state.json"
        )
        self._lock = RLock()

    def _read_system(self) -> dict[str, Any]:
        if not self.path.exists():
            system = seed_system()
            self._write_system(system)
            return system
        return _normalize_system(
            json.loads(self.path.read_text(encoding="utf-8"))
        )

    def _write_system(self, system: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(system, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        temporary.replace(self.path)

    def reset_all(self) -> dict[str, Any]:
        with self._lock:
            system = seed_system()
            self._write_system(system)
            return deepcopy(system)

    def reset(self, scenario_id: str = DEFAULT_SCENARIO) -> dict[str, Any]:
        with self._lock:
            system = self._read_system()
            system, state = _reset_scenario_in_system(system, scenario_id)
            self._write_system(system)
            return deepcopy(state)

    def load(self, scenario_id: str = DEFAULT_SCENARIO) -> dict[str, Any]:
        system = self._read_system()
        if scenario_id not in system["scenarios"]:
            raise KeyError(f"Unknown scenario: {scenario_id}")
        return deepcopy(system["scenarios"][scenario_id])

    def save(
        self, state: dict[str, Any], scenario_id: str = DEFAULT_SCENARIO
    ) -> None:
        with self._lock:
            system = self._read_system()
            system["scenarios"][scenario_id] = deepcopy(state)
            self._write_system(system)

    def snapshot(self, scenario_id: str = DEFAULT_SCENARIO) -> dict[str, Any]:
        return self.load(scenario_id)

    def system_snapshot(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._read_system())

    def mutate(
        self,
        mutation: Callable[[dict[str, Any]], tuple[dict[str, Any], MutationResult]],
        scenario_id: str = DEFAULT_SCENARIO,
    ) -> MutationResult:
        """Apply one scenario transition under a process-local lock."""
        with self._lock:
            system = self._read_system()
            state = deepcopy(system["scenarios"][scenario_id])
            updated, result = mutation(state)
            system["scenarios"][scenario_id] = updated
            self._write_system(system)
            return result

    def mutate_system(
        self,
        mutation: Callable[[dict[str, Any]], tuple[dict[str, Any], MutationResult]],
    ) -> MutationResult:
        """Atomically transition scenarios and the persistent event ledger."""
        with self._lock:
            system = self._read_system()
            updated, result = mutation(deepcopy(system))
            self._write_system(updated)
            return result


_FIRESTORE_TRACE_RESULT_KEYS = (
    "status",
    "candidate_set_id",
    "safe_candidates_considered",
    "selected_candidate_id",
    "selection_reason_codes",
    "selector",
    "base_version",
    "final_version",
    "outcome",
    "outbox_status",
    "outbox_count",
    "messages_sent",
    "human_reason",
)


def _compact_trace_result(result: Any) -> Any:
    """Keep observable ADK evidence without recursively persisting event payloads."""
    if not isinstance(result, dict):
        if isinstance(result, (str, int, float, bool)) or result is None:
            return result
        return str(type(result).__name__)
    compact = {
        key: deepcopy(result[key])
        for key in _FIRESTORE_TRACE_RESULT_KEYS
        if key in result
    }
    reverified = result.get("deterministic_reverification")
    if isinstance(reverified, dict) and "passed" in reverified:
        compact["deterministic_reverification"] = {"passed": bool(reverified["passed"])}
    failure = result.get("failure")
    if isinstance(failure, dict):
        compact["failure"] = {
            key: failure[key]
            for key in ("type", "message")
            if key in failure
        }
    return compact


def _compact_agent_trace(trace: Any) -> list[dict[str, Any]]:
    """Bound persisted tool traces to the evidence needed by UI and E2E checks."""
    if not isinstance(trace, list):
        return []
    compact_trace: list[dict[str, Any]] = []
    for item in trace:
        if not isinstance(item, dict):
            continue
        compact: dict[str, Any] = {
            key: deepcopy(item[key])
            for key in ("type", "name")
            if key in item
        }
        if "arguments" in item and isinstance(item["arguments"], dict):
            compact["arguments"] = deepcopy(item["arguments"])
        if "result" in item:
            compact["result"] = _compact_trace_result(item["result"])
        compact_trace.append(compact)
    return compact_trace


def _compact_system_for_firestore(system: dict[str, Any]) -> dict[str, Any]:
    """Remove recursive/transient evidence before writing the single Firestore doc.

    Candidate summaries, the selected plan, metrics, reason codes, verification,
    versions and compact ADK tool evidence remain inspectable. The full candidate
    set is only needed while an event is non-terminal; persisting it after commit
    duplicates the selected plan and made the contest document exceed Firestore's
    1 MiB document limit under repeated demo/E2E runs.
    """
    compacted = deepcopy(system)
    for event in compacted.get("events", {}).values():
        if not isinstance(event, dict):
            continue
        if event.get("agent_trace") is not None:
            event["agent_trace"] = _compact_agent_trace(event["agent_trace"])
        if event.get("status") in TERMINAL_EVENT_STATUSES:
            event.pop("candidate_set", None)
    return compacted


class FirestoreRepository:
    """Single-document transactional store used by the contest deployment.

    Keeping the synthetic schedules and the event ledger in one document makes
    the schedule version, event terminal state, audit, and outbox one atomic
    write. Pub/Sub can redeliver freely without duplicating business effects.
    """

    def __init__(self, client: Any | None = None):
        if client is None:
            from google.cloud import firestore

            client = firestore.Client()
        self.client = client
        collection = os.environ.get(
            "PLACES_AGAIN_FIRESTORE_COLLECTION", "places_again"
        )
        document = os.environ.get(
            "PLACES_AGAIN_PRODUCTION_ID", "taskmaster-system"
        )
        self.document = client.collection(collection).document(document)

    @staticmethod
    def _decode(payload: dict[str, Any] | None) -> dict[str, Any]:
        if not payload:
            return seed_system()
        if "system" in payload:
            return _normalize_system(payload["system"])
        if "state" in payload:
            return _normalize_system(payload["state"])
        return _normalize_system(payload)

    @staticmethod
    def _encode(system: dict[str, Any]) -> dict[str, Any]:
        # `state` remains as a migration/read-compatibility view for v1.
        compacted = _compact_system_for_firestore(system)
        return {
            "system": compacted,
            "state": deepcopy(compacted["scenarios"][DEFAULT_SCENARIO]),
        }

    def reset_all(self) -> dict[str, Any]:
        system = seed_system()
        self.document.set(self._encode(system))
        return deepcopy(system)

    def reset(self, scenario_id: str = DEFAULT_SCENARIO) -> dict[str, Any]:
        def reset_in_transaction(
            system: dict[str, Any],
        ) -> tuple[dict[str, Any], dict[str, Any]]:
            return _reset_scenario_in_system(system, scenario_id)

        return self.mutate_system(reset_in_transaction)

    def system_snapshot(self) -> dict[str, Any]:
        snapshot = self.document.get()
        if not snapshot.exists:
            return self.reset_all()
        return deepcopy(self._decode(snapshot.to_dict() or {}))

    def load(self, scenario_id: str = DEFAULT_SCENARIO) -> dict[str, Any]:
        system = self.system_snapshot()
        if scenario_id not in system["scenarios"]:
            raise KeyError(f"Unknown scenario: {scenario_id}")
        return deepcopy(system["scenarios"][scenario_id])

    def save(
        self, state: dict[str, Any], scenario_id: str = DEFAULT_SCENARIO
    ) -> None:
        system = self.system_snapshot()
        system["scenarios"][scenario_id] = deepcopy(state)
        self.document.set(self._encode(system))

    def snapshot(self, scenario_id: str = DEFAULT_SCENARIO) -> dict[str, Any]:
        return self.load(scenario_id)

    def mutate(
        self,
        mutation: Callable[[dict[str, Any]], tuple[dict[str, Any], MutationResult]],
        scenario_id: str = DEFAULT_SCENARIO,
    ) -> MutationResult:
        def mutate_scenario(
            system: dict[str, Any],
        ) -> tuple[dict[str, Any], MutationResult]:
            updated, result = mutation(deepcopy(system["scenarios"][scenario_id]))
            system["scenarios"][scenario_id] = updated
            return system, result

        return self.mutate_system(mutate_scenario)

    def mutate_system(
        self,
        mutation: Callable[[dict[str, Any]], tuple[dict[str, Any], MutationResult]],
    ) -> MutationResult:
        """Apply a whole-system transition in a retry-safe transaction."""
        from google.cloud import firestore

        transaction = self.client.transaction()

        @firestore.transactional
        def apply_in_transaction(active_transaction):
            snapshot = self.document.get(transaction=active_transaction)
            payload = snapshot.to_dict() if snapshot.exists else None
            system = self._decode(payload)
            updated, result = mutation(deepcopy(system))
            active_transaction.set(self.document, self._encode(updated))
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
