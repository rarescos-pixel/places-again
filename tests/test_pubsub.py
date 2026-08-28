import base64
import json
import types

import pytest

import places_again.pubsub as pubsub_module
from places_again.pubsub import decode_event_id


def encoded(payload):
    return base64.b64encode(json.dumps(payload).encode()).decode()


def test_pubsub_payload_contains_only_opaque_event_id():
    event_id = "2469cc01-ae21-45de-af13-f845567743f7"
    assert decode_event_id(encoded({"event_id": event_id})) == event_id


@pytest.mark.parametrize(
    "payload", ["not-base64", encoded({"wrong": "field"}), encoded({"event_id": 7})]
)
def test_pubsub_payload_is_strictly_rejected(payload):
    with pytest.raises(ValueError, match="event"):
        decode_event_id(payload)


def test_publish_retries_and_returns_the_stable_event_id(monkeypatch):
    class Future:
        def __init__(self, should_fail):
            self.should_fail = should_fail

        def result(self, timeout):
            assert timeout == 10
            if self.should_fail:
                raise TimeoutError("temporary")
            return "pubsub-message-id"

    class Publisher:
        calls = 0

        def topic_path(self, project, topic):
            return f"projects/{project}/topics/{topic}"

        def publish(self, *_args, **_kwargs):
            self.calls += 1
            return Future(should_fail=self.calls == 1)

    publisher = Publisher()
    fake_pubsub = types.SimpleNamespace(PublisherClient=lambda: publisher)
    import google.cloud

    monkeypatch.setattr(google.cloud, "pubsub_v1", fake_pubsub, raising=False)
    monkeypatch.setattr(pubsub_module.time, "sleep", lambda _delay: None)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("PLACES_AGAIN_PUBSUB_TOPIC", "events")
    monkeypatch.setenv("PLACES_AGAIN_PUBSUB_RETRY_MAX_ATTEMPTS", "3")

    result = pubsub_module.publish_event("stable-event-id")

    assert result["event_id"] == "stable-event-id"
    assert result["message_id"] == "pubsub-message-id"
    assert result["publish_attempts"] == 2
