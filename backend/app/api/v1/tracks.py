from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.camera import Camera
from backend.app.models.track import Track

router = APIRouter(tags=["tracks"])
DatabaseSession = Annotated[Session, Depends(get_db)]


class TrackCreate(BaseModel):
    camera_id: int
    track_id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=80)
    status: str = Field(default="active", min_length=1, max_length=30)


class TrackResponse(TrackCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    started_at: datetime
    ended_at: datetime | None


@router.get("/tracks", response_model=list[TrackResponse])
def list_tracks(
    db: DatabaseSession,
    camera_id: int | None = None,
    active_only: bool = False,
) -> list[Track]:
    query = select(Track).order_by(Track.id)
    if camera_id is not None:
        query = query.where(Track.camera_id == camera_id)
    if active_only:
        query = query.where(Track.status == "active")
    return list(db.scalars(query))


@router.post(
    "/tracks",
    response_model=TrackResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_track(payload: TrackCreate, db: DatabaseSession) -> Track:
    if db.get(Camera, payload.camera_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")

    track = Track(**payload.model_dump())
    db.add(track)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A track with this identifier already exists.",
        ) from exc
    db.refresh(track)
    return track


@router.post("/tracks/{track_id}/close", response_model=TrackResponse)
def close_track(track_id: str, db: DatabaseSession) -> Track:
    track = db.scalar(select(Track).where(Track.track_id == track_id))
    if track is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found.")
    track.status = "closed"
    track.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(track)
    return track
