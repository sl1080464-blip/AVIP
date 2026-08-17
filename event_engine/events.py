from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class EventRecord:
    """Canonical event representation used by the risk engine and API."""

    event_type: str
    camera_id: str
    timestamp: datetime
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class EventEngine:
    """Abstract event orchestration layer.

    Concrete implementations should convert raw detection data into semantically rich
    event records and optionally publish alerts after risk scoring.
    """

    def process(self, raw_event: dict[str, Any]) -> EventRecord:
        return EventRecord(
            event_type=raw_event.get("event_type", "unknown"),
            camera_id=raw_event.get("camera_id", "unknown"),
            timestamp=raw_event.get("timestamp", datetime.now(timezone.utc)),
            confidence=float(raw_event.get("confidence", 0.0)),
            metadata=raw_event.get("metadata", {}),
        )
