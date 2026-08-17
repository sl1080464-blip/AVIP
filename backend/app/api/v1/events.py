from fastapi import APIRouter

router = APIRouter(tags=["events"])


@router.get("/events")
def list_events() -> list[dict[str, object]]:
    return [
        {
            "id": "evt-101",
            "event_type": "person_detected",
            "camera_id": "cam-01",
            "confidence": 0.94,
            "metadata": {"zone": "entrance"},
        },
        {
            "id": "evt-102",
            "event_type": "zone_entry",
            "camera_id": "cam-02",
            "confidence": 0.91,
            "metadata": {"zone": "parking-east"},
        },
    ]
