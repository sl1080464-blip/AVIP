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
from backend.app.models.zone import Zone

router = APIRouter(tags=["zones"])
DatabaseSession = Annotated[Session, Depends(get_db)]


class ZoneCreate(BaseModel):
    camera_id: int
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    polygon: str = Field(default="[]", max_length=500)
    x: float | None = None
    y: float | None = None


class ZoneUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    polygon: str | None = Field(default=None, max_length=500)
    x: float | None = None
    y: float | None = None


class ZoneResponse(ZoneCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


def _get_zone_or_404(zone_id: int, db: Session) -> Zone:
    zone = db.get(Zone, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found.")
    return zone


@router.get("/zones", response_model=list[ZoneResponse])
def list_zones(
    db: DatabaseSession,
    camera_id: int | None = None,
) -> list[Zone]:
    query = select(Zone).order_by(Zone.id)
    if camera_id is not None:
        query = query.where(Zone.camera_id == camera_id)
    return list(db.scalars(query))


@router.post(
    "/zones",
    response_model=ZoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_zone(
    payload: ZoneCreate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Zone:
    if db.get(Camera, payload.camera_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")
    existing = db.scalar(
        select(Zone).where(Zone.camera_id == payload.camera_id, Zone.name == payload.name)
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zone already exists.")

    zone = Zone(**payload.model_dump())
    db.add(zone)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Zone already exists.",
        ) from exc
    db.refresh(zone)
    return zone


@router.patch("/zones/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: int,
    payload: ZoneUpdate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Zone:
    zone = _get_zone_or_404(zone_id, db)
    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates:
        duplicate = db.scalar(
            select(Zone).where(
                Zone.camera_id == zone.camera_id,
                Zone.name == updates["name"],
                Zone.id != zone.id,
            )
        )
        if duplicate is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zone already exists.")
    for field, value in updates.items():
        setattr(zone, field, value)
    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    zone = _get_zone_or_404(zone_id, db)
    db.delete(zone)
    db.commit()
