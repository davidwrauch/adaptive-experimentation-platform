from collections import defaultdict

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import Event, MetricsSummary
from app.schemas import BehavioralMetric, PolicyMetric, SegmentRewardMetric
from app.services.simulation import segment_for_context


RECENT_WINDOW_LIMIT = 2_000


def update_metrics_summary(db: Session, events: list[Event]) -> None:
    policies = {event.policy for event in events}
    summaries = {
        summary.policy: summary
        for summary in db.query(MetricsSummary).filter(MetricsSummary.policy.in_(policies)).all()
    } if policies else {}

    for event in events:
        summary = summaries.get(event.policy)
        if summary is None:
            summary = MetricsSummary(
                policy=event.policy,
                event_count=0,
                cumulative_reward=0.0,
                cumulative_long_term_reward=0.0,
                fatigue_delta_sum=0.0,
                unsubscribe_risk_sum=0.0,
                unsubscribe_risk_delta_sum=0.0,
                assignments={},
            )
            db.add(summary)
            summaries[event.policy] = summary

        context = event.context or {}
        outcome = context.get("outcome", {})
        long_term_reward = float(outcome.get("long_term_reward", event.reward))
        fatigue_delta = float(outcome.get("fatigue_delta", 0.0))
        unsubscribe_risk_delta = float(outcome.get("unsubscribe_risk_delta", 0.0))
        unsubscribe_risk = float(context.get("unsubscribe_risk", 0.0)) + unsubscribe_risk_delta
        assignments = dict(summary.assignments or {})

        summary.event_count += 1
        summary.cumulative_reward += event.reward
        summary.cumulative_long_term_reward += long_term_reward
        summary.fatigue_delta_sum += fatigue_delta
        summary.unsubscribe_risk_sum += unsubscribe_risk
        summary.unsubscribe_risk_delta_sum += unsubscribe_risk_delta
        assignments[event.action] = int(assignments.get(event.action, 0)) + 1
        summary.assignments = assignments


def clear_metrics_summary(db: Session) -> None:
    db.query(MetricsSummary).delete()


def ensure_metrics_summary(db: Session) -> None:
    summary_count = db.query(func.count(MetricsSummary.policy)).scalar() or 0
    if summary_count:
        return

    first_event_id = db.query(Event.id).limit(1).scalar()
    if first_event_id is None:
        return

    for chunk in _event_chunks(db):
        update_metrics_summary(db, chunk)
    db.commit()


def summary_policy_metrics(db: Session) -> list[PolicyMetric]:
    ensure_metrics_summary(db)
    rows = db.query(MetricsSummary).order_by(MetricsSummary.policy).all()
    policies = []
    for row in rows:
        count = max(1, row.event_count)
        policies.append(
            PolicyMetric(
                policy=row.policy,
                event_count=row.event_count,
                cumulative_reward=round(row.cumulative_reward, 4),
                average_reward=round(row.cumulative_reward / count, 4),
                assignments=row.assignments or {},
                behavioral=BehavioralMetric(
                    cumulative_immediate_reward=round(row.cumulative_reward, 4),
                    cumulative_long_term_reward=round(row.cumulative_long_term_reward, 4),
                    average_immediate_reward=round(row.cumulative_reward / count, 4),
                    average_long_term_reward=round(row.cumulative_long_term_reward / count, 4),
                    average_fatigue_delta=round(row.fatigue_delta_sum / count, 4),
                    average_unsubscribe_risk=round(row.unsubscribe_risk_sum / count, 4),
                    average_unsubscribe_risk_delta=round(row.unsubscribe_risk_delta_sum / count, 4),
                    reward_by_segment=[],
                ),
            )
        )
    return policies


def total_events_from_summary(db: Session) -> int:
    ensure_metrics_summary(db)
    return int(db.query(func.coalesce(func.sum(MetricsSummary.event_count), 0)).scalar() or 0)


def latest_event_timestamp(db: Session):
    return db.query(func.max(Event.created_at)).scalar()


def recent_events(db: Session, limit: int = RECENT_WINDOW_LIMIT) -> list[Event]:
    safe_limit = max(1, min(limit, RECENT_WINDOW_LIMIT))
    return db.query(Event).order_by(desc(Event.created_at), desc(Event.id)).limit(safe_limit).all()


def attach_recent_behavioral_segments(policies: list[PolicyMetric], events: list[Event]) -> None:
    segment_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    segment_immediate_rewards: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    segment_long_term_rewards: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for event in events:
        context = event.context or {}
        outcome = context.get("outcome", {})
        segment = segment_for_context(context)
        long_term_reward = float(outcome.get("long_term_reward", event.reward))
        segment_counts[event.policy][segment] += 1
        segment_immediate_rewards[event.policy][segment] += event.reward
        segment_long_term_rewards[event.policy][segment] += long_term_reward

    for policy in policies:
        if policy.behavioral is None:
            continue
        policy.behavioral.reward_by_segment = [
            SegmentRewardMetric(
                segment=segment,
                event_count=segment_counts[policy.policy][segment],
                average_immediate_reward=round(
                    segment_immediate_rewards[policy.policy][segment]
                    / segment_counts[policy.policy][segment],
                    4,
                ),
                average_long_term_reward=round(
                    segment_long_term_rewards[policy.policy][segment]
                    / segment_counts[policy.policy][segment],
                    4,
                ),
            )
            for segment in sorted(segment_counts[policy.policy])
        ]


def _event_chunks(db: Session, size: int = 1_000):
    offset = 0
    while True:
        events = db.query(Event).order_by(Event.id).offset(offset).limit(size).all()
        if not events:
            break
        yield events
        offset += size
