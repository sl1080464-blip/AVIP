from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.models.alert import Alert
from backend.app.models.event import Event
from backend.app.models.user import User

router = APIRouter(tags=["alerts"])
DatabaseSession = Annotated[Session, Depends(get_db)]


class AlertCreate(BaseModel):
    event_id: int
    level: str = Field(default="medium", min_length=1, max_length=30)
    message: str = Field(min_length=1, max_length=255)


class AlertResponse(AlertCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    acknowledged: bool


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    db: DatabaseSession,
    acknowledged: bool | None = None,
    camera_id: int | None = None,
) -> list[Alert]:
    query = select(Alert).join(Event).order_by(Alert.id)
    if acknowledged is not None:
        query = query.where(Alert.acknowledged == acknowledged)
    if camera_id is not None:
        query = query.where(Event.camera_id == camera_id)
    return list(db.scalars(query))


@router.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(
    payload: AlertCreate,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Alert:
    if db.get(Event, payload.event_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    db: DatabaseSession,
    _: Annotated[User, Depends(get_current_user)],
) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert
