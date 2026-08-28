import base64
import json

import pytest

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
