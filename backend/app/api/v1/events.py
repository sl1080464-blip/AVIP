from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.camera import Camera
from backend.app.models.event import Event
from backend.app.models.user import User

router = APIRouter(tags=["events"])
DatabaseSession = Annotated[Session, Depends(get_db)]


class EventCreate(BaseModel):
    camera_id: int
    event_type: str = Field(min_length=1, max_length=80)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: dict[str, object] = Field(default_factory=dict)


class EventResponse(EventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @classmethod
    def from_model(cls, event: Event) -> "EventResponse":
        return cls(
            id=event.id,
            camera_id=event.camera_id,
            event_type=event.event_type,
            confidence=event.confidence,
            metadata=event.event_metadata,
        )


@router.get("/events", response_model=list[EventResponse])
def list_events(
    db: DatabaseSession,
    camera_id: int | None = None,
) -> list[EventResponse]:
    query = select(Event).order_by(Event.id)
    if camera_id is not None:
        query = query.where(Event.camera_id == camera_id)
    return [EventResponse.from_model(event) for event in db.scalars(query)]


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    payload: EventCreate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> EventResponse:
    if db.get(Camera, payload.camera_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found.")

    event = Event(
        camera_id=payload.camera_id,
        event_type=payload.event_type,
        confidence=payload.confidence,
        event_metadata=payload.metadata,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventResponse.from_model(event)
