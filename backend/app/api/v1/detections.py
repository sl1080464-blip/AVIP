from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.camera import Camera
from backend.app.models.detection import Detection
from backend.app.models.track import Track
from backend.app.models.user import User
from backend.app.services.detection_service import DetectionService

router = APIRouter(tags=["detections"])
service = DetectionService()
DatabaseSession = Annotated[Session, Depends(get_db)]


class DetectionCreate(BaseModel):
    camera_id: int
    label: str = Field(min_length=1, max_length=80)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    track_id: str | None = Field(default=None, max_length=80)
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None


class DetectionResponse(DetectionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


@router.get("/detections", response_model=list[DetectionResponse])
def list_detections(
    db: DatabaseSession,
    camera_id: int | None = None,
) -> list[Detection]:
    query = select(Detection).order_by(Detection.id)
    if camera_id is not None:
        query = query.where(Detection.camera_id == camera_id)
    return list(db.scalars(query))


@router.post(
    "/detections",
    response_model=DetectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_detection(
    payload: DetectionCreate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Detection:
    if db.get(Camera, payload.camera_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")
    if payload.track_id is not None:
        track = db.scalar(select(Track).where(Track.track_id == payload.track_id))
        if track is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found.")
        if track.camera_id != payload.camera_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Track belongs to a different camera.",
            )

    detection = Detection(**payload.model_dump())
    db.add(detection)
    db.commit()
    db.refresh(detection)
    return detection


@router.post(
    "/detections/demo",
    response_model=list[DetectionResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_demo_detections(
    camera_id: int,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> list[Detection]:
    if db.get(Camera, camera_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")

    detections = [
        Detection(
            camera_id=camera_id,
            label=item.label,
            confidence=item.confidence,
            x=item.x,
            y=item.y,
            width=item.width,
            height=item.height,
        )
        for item in service.detect(frame={"source": "demo"})
    ]
    db.add_all(detections)
    db.commit()
    for detection in detections:
        db.refresh(detection)
    return detections
