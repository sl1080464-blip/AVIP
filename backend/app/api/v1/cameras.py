from fastapi import APIRouter

router = APIRouter(tags=["cameras"])


@router.get("/cameras")
def list_cameras() -> list[dict[str, str]]:
    return [
        {
            "id": "cam-01",
            "name": "North Entrance",
            "status": "online",
            "stream_url": "rtsp://camera-01/stream",
        },
        {
            "id": "cam-02",
            "name": "Parking Lot",
            "status": "online",
            "stream_url": "rtsp://camera-02/stream",
        },
    ]
