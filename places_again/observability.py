from __future__ import annotations

import json
import logging
from typing import Any


LOGGER = logging.getLogger("places_again")


def emit(event: str, **fields: Any) -> None:
    """Emit Cloud Logging-friendly observable facts, never model reasoning."""
    payload = {"event": event, **fields}
    LOGGER.info(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
