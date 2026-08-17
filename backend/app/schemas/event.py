from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    PERSON_DETECTED = "person_detected"
    VEHICLE_DETECTED = "vehicle_detected"
    FACE_DETECTED = "face_detected"
    ZONE_ENTRY = "zone_entry"
    ZONE_EXIT = "zone_exit"
    LINE_CROSSING = "line_crossing"
    PROLONGED_PRESENCE = "prolonged_presence"
    ABANDONED_OBJECT = "abandoned_object"
    DANGEROUS_OBJECT_DETECTED = "dangerous_object_detected"


class EventSchema(BaseModel):
    event_type: EventType
    camera_id: str
    timestamp: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
