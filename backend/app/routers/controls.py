from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import PolicyControlUpdate
from app.services.rollout import (
    list_policy_controls,
    pause_policy_control,
    resume_policy_control,
    rollout_recommendation,
    update_policy_control,
)
from app.services.streaming import streaming_status

router = APIRouter(prefix="/controls", tags=["controls"])


@router.get("/policies")
def get_policy_controls(db: Session = Depends(get_db)) -> dict:
    return {"policies": [asdict(control) for control in list_policy_controls(db)]}


@router.post("/policies/{policy}")
def update_policy_control_endpoint(
    policy: str,
    payload: PolicyControlUpdate,
    db: Session = Depends(get_db),
) -> dict:
    control = update_policy_control(
        db,
        policy,
        traffic_cap=payload.traffic_cap,
        canary_percentage=payload.canary_percentage,
    )
    return asdict(control)


@router.post("/policies/{policy}/pause")
def pause_policy(policy: str, db: Session = Depends(get_db)) -> dict:
    return asdict(pause_policy_control(db, policy))


@router.post("/policies/{policy}/resume")
def resume_policy(policy: str, db: Session = Depends(get_db)) -> dict:
    return asdict(resume_policy_control(db, policy))


@router.get("/rollout/recommendation")
def get_rollout_recommendation(db: Session = Depends(get_db)) -> dict:
    events = db.query(Event).all()
    return rollout_recommendation(events)


@router.get("/streaming/status")
def get_streaming_status() -> dict:
    return asdict(streaming_status())
