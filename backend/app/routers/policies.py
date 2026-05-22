from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, PolicyVersion
from app.schemas import (
    DecisionRequest,
    DecisionResponse,
    EventRead,
    PolicyPromotionRequest,
    PolicyRollbackRequest,
    PolicyVersionCreate,
    PolicyVersionRead,
)
from app.services.metrics_summary import update_metrics_summary
from app.services.policy_engine import policy_engine
from app.services.simulation import build_intervention, simulate_intervention_outcome

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("")
def list_policies() -> dict[str, list[str]]:
    return {"policies": ["static", "epsilon_greedy", "thompson_sampling", "linucb"]}


@router.get("/versions", response_model=list[PolicyVersionRead])
def list_policy_versions(db: Session = Depends(get_db)) -> list[PolicyVersion]:
    return db.query(PolicyVersion).order_by(PolicyVersion.policy_name, PolicyVersion.version).all()


@router.post("/versions", response_model=PolicyVersionRead)
def create_policy_version(payload: PolicyVersionCreate, db: Session = Depends(get_db)) -> PolicyVersion:
    version = PolicyVersion(**payload.model_dump())
    if version.status == "champion":
        version.deployed_at = datetime.now(timezone.utc)
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.post("/promote", response_model=PolicyVersionRead)
def promote_policy(payload: PolicyPromotionRequest, db: Session = Depends(get_db)) -> PolicyVersion:
    version = _find_version(db, payload.policy_name, payload.version)
    for existing in db.query(PolicyVersion).filter(PolicyVersion.policy_name == payload.policy_name).all():
        if existing.id == version.id:
            existing.status = "champion"
            existing.deployed_at = datetime.now(timezone.utc)
            existing.notes = payload.operator_reason or existing.notes
        elif existing.status == "champion":
            existing.status = "challenger"
    db.commit()
    db.refresh(version)
    return version


@router.post("/rollback", response_model=PolicyVersionRead)
def rollback_policy(payload: PolicyRollbackRequest, db: Session = Depends(get_db)) -> PolicyVersion:
    current = (
        db.query(PolicyVersion)
        .filter(PolicyVersion.policy_name == payload.policy_name, PolicyVersion.status == "champion")
        .first()
    )
    target_version = payload.target_version or (current.rollback_target if current else None)
    if not target_version:
        raise HTTPException(status_code=400, detail="No rollback target configured")
    target = _find_version(db, payload.policy_name, target_version)
    if current:
        current.status = "archived"
    target.status = "champion"
    target.deployed_at = datetime.now(timezone.utc)
    target.notes = payload.operator_reason or target.notes
    db.commit()
    db.refresh(target)
    return target


@router.post("/decide", response_model=DecisionResponse)
def decide(payload: DecisionRequest) -> DecisionResponse:
    action, propensity = policy_engine.choose(payload.policy, payload.context, payload.actions)
    return DecisionResponse(policy=payload.policy, action=action, propensity=propensity)


@router.post("/simulate", response_model=EventRead)
def simulate_decision(payload: DecisionRequest, db: Session = Depends(get_db)) -> Event:
    action, propensity = policy_engine.choose(payload.policy, payload.context, payload.actions)
    intervention = build_intervention(action, payload.policy)
    outcome = simulate_intervention_outcome(payload.context, intervention)
    reward = outcome["immediate_reward"]
    event = Event(
        user_id=payload.user_id,
        policy=payload.policy,
        action=action,
        reward=reward,
        propensity=propensity,
        context={
            **payload.context,
            "intervention": intervention,
            "outcome": outcome,
        },
    )
    db.add(event)
    update_metrics_summary(db, [event])
    db.commit()
    db.refresh(event)
    policy_engine.update(payload.policy, action, reward)
    return event


def _find_version(db: Session, policy_name: str, version: str) -> PolicyVersion:
    policy_version = (
        db.query(PolicyVersion)
        .filter(PolicyVersion.policy_name == policy_name, PolicyVersion.version == version)
        .first()
    )
    if policy_version is None:
        raise HTTPException(status_code=404, detail="Policy version not found")
    return policy_version
