from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import DecisionRequest, DecisionResponse, EventRead
from app.services.policy_engine import policy_engine
from app.services.simulation import build_intervention, simulate_intervention_outcome

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("")
def list_policies() -> dict[str, list[str]]:
    return {"policies": ["static", "epsilon_greedy", "thompson_sampling", "linucb"]}


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
    db.commit()
    db.refresh(event)
    policy_engine.update(payload.policy, action, reward)
    return event
