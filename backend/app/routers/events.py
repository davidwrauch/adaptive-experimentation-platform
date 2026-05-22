from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventRead
from app.services.metrics_summary import update_metrics_summary
from app.services.policy_engine import policy_engine

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventRead)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> Event:
    event = Event(**payload.model_dump())
    db.add(event)
    update_metrics_summary(db, [event])
    db.commit()
    db.refresh(event)
    policy_engine.update(event.policy, event.action, event.reward)
    return event


@router.get("", response_model=list[EventRead])
def list_events(limit: int = 100, db: Session = Depends(get_db)) -> list[Event]:
    safe_limit = max(1, min(limit, 250))
    return db.query(Event).order_by(desc(Event.created_at), desc(Event.id)).limit(safe_limit).all()


@router.get("/recent", response_model=list[EventRead])
def recent_events(limit: int = 50, db: Session = Depends(get_db)) -> list[Event]:
    safe_limit = max(1, min(limit, 250))
    return db.query(Event).order_by(desc(Event.created_at), desc(Event.id)).limit(safe_limit).all()
