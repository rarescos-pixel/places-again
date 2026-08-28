from __future__ import annotations

import base64
import json
import os
import random
import time
from typing import Any


def _publish_retry_delay(attempt: int) -> float:
    base = min(
        0.5,
        max(0.01, float(os.environ.get("PLACES_AGAIN_PUBSUB_RETRY_BASE_SECONDS", "0.25"))),
    )
    cap = min(
        2.0,
        max(base, float(os.environ.get("PLACES_AGAIN_PUBSUB_RETRY_CAP_SECONDS", "2"))),
    )
    return min(cap, base * (2 ** (attempt - 1))) + random.uniform(0, base)


def _publish_max_attempts() -> int:
    try:
        return min(
            4,
            max(1, int(os.environ.get("PLACES_AGAIN_PUBSUB_RETRY_MAX_ATTEMPTS", "4"))),
        )
    except ValueError:
        return 4


def _publish_attempt_timeout() -> float:
    try:
        configured = os.environ.get("PLACES_AGAIN_PUBSUB_PUBLISH_TIMEOUT", "10")
        return min(10.0, max(1.0, float(configured)))
    except ValueError:
        return 10.0


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
    max_attempts = _publish_max_attempts()
    attempt_timeout = _publish_attempt_timeout()
    for attempt in range(1, max_attempts + 1):
        try:
            message_id = publisher.publish(
                topic_path,
                payload,
                event_id=event_id,
                correlation_id=event_id,
            ).result(timeout=attempt_timeout)
            break
        except Exception:
            if attempt == max_attempts:
                raise
            time.sleep(_publish_retry_delay(attempt))
    return {
        "mode": "google_pubsub",
        "event_id": event_id,
        "message_id": message_id,
        "topic": topic_path,
        "publish_attempts": attempt,
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
