from __future__ import annotations

import base64
import json
import os
from typing import Any


def publish_event(event_id: str) -> dict[str, Any]:
    """Publish only an opaque event id; incident text remains in Firestore."""
    topic = os.environ.get("PLACES_AGAIN_PUBSUB_TOPIC")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not topic or not project:
        return {"mode": "local_background", "event_id": event_id}

    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic_path = (
        topic if topic.startswith("projects/") else publisher.topic_path(project, topic)
    )
    payload = json.dumps({"event_id": event_id}, separators=(",", ":")).encode()
    message_id = publisher.publish(
        topic_path,
        payload,
        event_id=event_id,
        correlation_id=event_id,
    ).result(timeout=15)
    return {
        "mode": "google_pubsub",
        "event_id": event_id,
        "message_id": message_id,
        "topic": topic_path,
    }


def decode_event_id(encoded_data: str) -> str:
    try:
        decoded = base64.b64decode(encoded_data, validate=True)
        payload = json.loads(decoded.decode("utf-8"))
        event_id = payload["event_id"]
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as error:
        raise ValueError("invalid Pub/Sub event payload") from error
    if not isinstance(event_id, str) or len(event_id) > 64:
        raise ValueError("invalid event_id")
    return event_id
