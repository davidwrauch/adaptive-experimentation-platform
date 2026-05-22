from collections import defaultdict
from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.schemas import MetricsResponse, PolicyMetric
from app.services.bayesian import beta_binomial_policy_comparison
from app.services.exploration import exploration_saturation_metrics
from app.services.governance import label_policy
from app.services.monitoring import run_observability_checks
from app.services.ope import estimate_policy_value
from app.services.rollout import list_policy_controls, rollout_recommendation
from app.services.simulation import segment_for_context
from app.services.streaming import streaming_status

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)) -> MetricsResponse:
    events = db.query(Event).all()
    rewards: dict[str, float] = defaultdict(float)
    long_term_rewards: dict[str, float] = defaultdict(float)
    fatigue_deltas: dict[str, float] = defaultdict(float)
    unsubscribe_risks: dict[str, float] = defaultdict(float)
    unsubscribe_risk_deltas: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    assignments: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    segment_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    segment_immediate_rewards: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    segment_long_term_rewards: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for event in events:
        context = event.context or {}
        outcome = context.get("outcome", {})
        long_term_reward = float(outcome.get("long_term_reward", event.reward))
        fatigue_delta = float(outcome.get("fatigue_delta", 0.0))
        unsubscribe_risk_delta = float(outcome.get("unsubscribe_risk_delta", 0.0))
        unsubscribe_risk = float(context.get("unsubscribe_risk", 0.0)) + unsubscribe_risk_delta
        segment = segment_for_context(context)

        counts[event.policy] += 1
        rewards[event.policy] += event.reward
        long_term_rewards[event.policy] += long_term_reward
        fatigue_deltas[event.policy] += fatigue_delta
        unsubscribe_risks[event.policy] += unsubscribe_risk
        unsubscribe_risk_deltas[event.policy] += unsubscribe_risk_delta
        assignments[event.policy][event.action] += 1
        segment_counts[event.policy][segment] += 1
        segment_immediate_rewards[event.policy][segment] += event.reward
        segment_long_term_rewards[event.policy][segment] += long_term_reward

    policies = []
    for policy in sorted(counts):
        average_reward = rewards[policy] / counts[policy]
        traffic_share = counts[policy] / len(events) if events else 0.0
        ope = estimate_policy_value(events, policy)
        governance = label_policy(average_reward, traffic_share, ope)
        policies.append(
            PolicyMetric(
                policy=policy,
                event_count=counts[policy],
                cumulative_reward=round(rewards[policy], 4),
                average_reward=round(average_reward, 4),
                assignments=dict(assignments[policy]),
                ope=asdict(ope),
                governance=asdict(governance),
                behavioral={
                    "cumulative_immediate_reward": round(rewards[policy], 4),
                    "cumulative_long_term_reward": round(long_term_rewards[policy], 4),
                    "average_immediate_reward": round(average_reward, 4),
                    "average_long_term_reward": round(long_term_rewards[policy] / counts[policy], 4),
                    "average_fatigue_delta": round(fatigue_deltas[policy] / counts[policy], 4),
                    "average_unsubscribe_risk": round(unsubscribe_risks[policy] / counts[policy], 4),
                    "average_unsubscribe_risk_delta": round(
                        unsubscribe_risk_deltas[policy] / counts[policy], 4
                    ),
                    "reward_by_segment": [
                        {
                            "segment": segment,
                            "event_count": segment_counts[policy][segment],
                            "average_immediate_reward": round(
                                segment_immediate_rewards[policy][segment]
                                / segment_counts[policy][segment],
                                4,
                            ),
                            "average_long_term_reward": round(
                                segment_long_term_rewards[policy][segment]
                                / segment_counts[policy][segment],
                                4,
                            ),
                        }
                        for segment in sorted(segment_counts[policy])
                    ],
                },
            )
        )
    return MetricsResponse(
        total_events=len(events),
        policies=policies,
        observability=run_observability_checks(events),
        streaming=asdict(streaming_status()),
        rollout={
            "controls": [asdict(control) for control in list_policy_controls(db)],
            "rollback": rollout_recommendation(events),
        },
        exploration=exploration_saturation_metrics(events),
        bayesian=beta_binomial_policy_comparison(events),
    )
