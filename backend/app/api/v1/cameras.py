from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.camera import Camera
from backend.app.models.user import User


class CameraCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    stream_url: str = Field(min_length=1, max_length=255)
    status: str = Field(default="online", min_length=1, max_length=30)
    description: str | None = None


class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    stream_url: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = Field(default=None, min_length=1, max_length=30)
    description: str | None = None


class CameraResponse(CameraCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


router = APIRouter(tags=["cameras"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/cameras", response_model=list[CameraResponse])
def list_cameras(db: DatabaseSession) -> list[Camera]:
    return list(db.scalars(select(Camera).order_by(Camera.id)))


@router.post(
    "/cameras",
    response_model=CameraResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_camera(
    payload: CameraCreate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Camera:
    camera = Camera(**payload.model_dump())
    db.add(camera)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A camera with this name already exists.",
        ) from exc
    db.refresh(camera)
    return camera


@router.get("/cameras/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: DatabaseSession) -> Camera:
    camera = db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")
    return camera


@router.patch("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Camera:
    camera = db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(camera, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A camera with this name already exists.",
        ) from exc
    db.refresh(camera)
    return camera


@router.delete("/cameras/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
    camera_id: int,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    camera = db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")
    if camera.zones or camera.detections or camera.events:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Camera cannot be deleted while it has related data.",
        )
    db.delete(camera)
    db.commit()
