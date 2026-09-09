from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.alert import Alert
from backend.app.models.event import Event

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
def list_alerts(db: DatabaseSession) -> list[Alert]:
    return list(db.scalars(select(Alert).order_by(Alert.id)))


@router.post(
    "/alerts",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(payload: AlertCreate, db: DatabaseSession) -> Alert:
    if db.get(Event, payload.event_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: int, db: DatabaseSession) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert
