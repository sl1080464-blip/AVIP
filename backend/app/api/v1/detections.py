from fastapi import APIRouter

from backend.app.services.detection_service import DetectionService

router = APIRouter(tags=["detections"])
service = DetectionService()


@router.get("/detections")
def list_detections() -> list[dict[str, object]]:
    return [
        {
            "label": item.label,
            "confidence": item.confidence,
            "x": item.x,
            "y": item.y,
            "width": item.width,
            "height": item.height,
            "metadata": item.metadata,
        }
        for item in service.detect(frame={"source": "demo"})
    ]


@router.post("/detections")
def create_detection() -> dict[str, object]:
    item = service.detect(frame={"source": "demo"})[0]
    return {
        "label": item.label,
        "confidence": item.confidence,
        "x": item.x,
        "y": item.y,
        "width": item.width,
        "height": item.height,
    }
