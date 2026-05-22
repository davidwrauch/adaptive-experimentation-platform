from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import PolicyControlUpdate
from app.services.rollout import rollout_recommendation, rollout_store
from app.services.streaming import streaming_status

router = APIRouter(prefix="/controls", tags=["controls"])


@router.get("/policies")
def list_policy_controls() -> dict:
    return {"policies": [asdict(control) for control in rollout_store.list_controls()]}


@router.post("/policies/{policy}")
def update_policy_control(policy: str, payload: PolicyControlUpdate) -> dict:
    control = rollout_store.update(
        policy,
        traffic_cap=payload.traffic_cap,
        canary_percentage=payload.canary_percentage,
    )
    return asdict(control)


@router.post("/policies/{policy}/pause")
def pause_policy(policy: str) -> dict:
    return asdict(rollout_store.pause(policy))


@router.post("/policies/{policy}/resume")
def resume_policy(policy: str) -> dict:
    return asdict(rollout_store.resume(policy))


@router.get("/rollout/recommendation")
def get_rollout_recommendation(db: Session = Depends(get_db)) -> dict:
    events = db.query(Event).all()
    return rollout_recommendation(events)


@router.get("/streaming/status")
def get_streaming_status() -> dict:
    return asdict(streaming_status())
