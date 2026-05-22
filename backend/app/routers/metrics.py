from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import GovernanceMetric, MetricsResponse, OpeMetric
from app.services.bayesian import beta_binomial_policy_comparison
from app.services.exploration import exploration_saturation_metrics
from app.services.governance import label_policy
from app.services.metrics_summary import (
    RECENT_WINDOW_LIMIT,
    attach_recent_behavioral_segments,
    latest_event_timestamp,
    recent_events,
    summary_policy_metrics,
    total_events_from_summary,
)
from app.services.monitoring import run_observability_checks
from app.services.ope import estimate_policy_value
from app.services.rollout import list_policy_controls, rollout_recommendation
from app.services.streaming import streaming_status

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsResponse)
def get_metrics_summary(db: Session = Depends(get_db)) -> MetricsResponse:
    events = recent_events(db, limit=RECENT_WINDOW_LIMIT)
    policies = summary_policy_metrics(db)
    attach_recent_behavioral_segments(policies, events)
    _attach_capped_policy_decisions(policies, events)
    return _metrics_response(db, policies, events)


@router.get("/details", response_model=MetricsResponse)
def get_metrics_details(db: Session = Depends(get_db)) -> MetricsResponse:
    events = recent_events(db, limit=RECENT_WINDOW_LIMIT)
    policies = summary_policy_metrics(db)
    attach_recent_behavioral_segments(policies, events)
    _attach_capped_policy_decisions(policies, events)
    return _metrics_response(db, policies, events)


@router.get("", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    return get_metrics_details(db)


def _metrics_response(db: Session, policies, capped_events) -> MetricsResponse:
    return MetricsResponse(
        total_events=total_events_from_summary(db),
        policies=policies,
        latest_timestamp=latest_event_timestamp(db),
        observability=run_observability_checks(capped_events),
        streaming=asdict(streaming_status()),
        rollout={
            "controls": [asdict(control) for control in list_policy_controls(db)],
            "rollback": rollout_recommendation(capped_events),
        },
        exploration=exploration_saturation_metrics(capped_events),
        bayesian=beta_binomial_policy_comparison(capped_events),
    )


def _attach_capped_policy_decisions(policies, capped_events) -> None:
    total_events = max(1, sum(item.event_count for item in policies))
    for policy in policies:
        traffic_share = policy.event_count / total_events
        ope = estimate_policy_value(capped_events, policy.policy)
        governance = label_policy(policy.average_reward, traffic_share, ope)
        policy.ope = OpeMetric(**asdict(ope))
        policy.governance = GovernanceMetric(**asdict(governance))
