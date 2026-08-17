from datetime import datetime, timezone

from backend.app.schemas.event import EventSchema, EventType


def test_event_schema_accepts_expected_fields() -> None:
    event = EventSchema(
        event_type=EventType.PERSON_DETECTED,
        camera_id="cam-01",
        timestamp=datetime.now(timezone.utc),
        confidence=0.92,
        metadata={"track_id": "t-100"},
    )

    assert event.event_type == EventType.PERSON_DETECTED
    assert event.metadata["track_id"] == "t-100"
