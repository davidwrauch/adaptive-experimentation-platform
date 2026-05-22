from collections import defaultdict

from sqlalchemy import desc, func
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models import Event, MetricsSummary
from app.schemas import BehavioralMetric, PolicyMetric, SegmentRewardMetric
from app.services.simulation import segment_for_context


RECENT_WINDOW_LIMIT = 2_000


def update_metrics_summary(db: Session, events: list[Event]) -> None:
    aggregates: dict[str, dict] = {}
    for event in events:
        aggregate = aggregates.setdefault(
            event.policy,
            {
                "event_count": 0,
                "cumulative_reward": 0.0,
                "cumulative_long_term_reward": 0.0,
                "fatigue_delta_sum": 0.0,
                "unsubscribe_risk_sum": 0.0,
                "unsubscribe_risk_delta_sum": 0.0,
                "assignments": {},
            },
        )

        context = event.context or {}
        outcome = context.get("outcome", {})
        long_term_reward = float(outcome.get("long_term_reward", event.reward))
        fatigue_delta = float(outcome.get("fatigue_delta", 0.0))
        unsubscribe_risk_delta = float(outcome.get("unsubscribe_risk_delta", 0.0))
        unsubscribe_risk = float(context.get("unsubscribe_risk", 0.0)) + unsubscribe_risk_delta

        aggregate["event_count"] += 1
        aggregate["cumulative_reward"] += event.reward
        aggregate["cumulative_long_term_reward"] += long_term_reward
        aggregate["fatigue_delta_sum"] += fatigue_delta
        aggregate["unsubscribe_risk_sum"] += unsubscribe_risk
        aggregate["unsubscribe_risk_delta_sum"] += unsubscribe_risk_delta
        aggregate["assignments"][event.action] = int(aggregate["assignments"].get(event.action, 0)) + 1

    for policy, aggregate in aggregates.items():
        existing_assignments = _existing_assignments(db, policy)
        merged_assignments = dict(existing_assignments)
        for action, count in aggregate["assignments"].items():
            merged_assignments[action] = int(merged_assignments.get(action, 0)) + count
        _upsert_metrics_summary(db, policy, aggregate, merged_assignments)


def clear_metrics_summary(db: Session) -> None:
    db.query(MetricsSummary).delete()


def _existing_assignments(db: Session, policy: str) -> dict:
    assignments = db.query(MetricsSummary.assignments).filter(MetricsSummary.policy == policy).scalar()
    return dict(assignments or {})


def _upsert_metrics_summary(db: Session, policy: str, aggregate: dict, assignments: dict) -> None:
    values = {
        "policy": policy,
        "event_count": aggregate["event_count"],
        "cumulative_reward": aggregate["cumulative_reward"],
        "cumulative_long_term_reward": aggregate["cumulative_long_term_reward"],
        "fatigue_delta_sum": aggregate["fatigue_delta_sum"],
        "unsubscribe_risk_sum": aggregate["unsubscribe_risk_sum"],
        "unsubscribe_risk_delta_sum": aggregate["unsubscribe_risk_delta_sum"],
        "assignments": assignments,
    }
    dialect_name = db.get_bind().dialect.name
    if dialect_name == "postgresql":
        statement = postgres_insert(MetricsSummary).values(**values)
    elif dialect_name == "sqlite":
        statement = sqlite_insert(MetricsSummary).values(**values)
    else:
        _fallback_upsert_metrics_summary(db, values)
        return

    excluded = statement.excluded
    db.execute(
        statement.on_conflict_do_update(
            index_elements=[MetricsSummary.policy],
            set_={
                "event_count": MetricsSummary.event_count + excluded.event_count,
                "cumulative_reward": MetricsSummary.cumulative_reward + excluded.cumulative_reward,
                "cumulative_long_term_reward": (
                    MetricsSummary.cumulative_long_term_reward + excluded.cumulative_long_term_reward
                ),
                "fatigue_delta_sum": MetricsSummary.fatigue_delta_sum + excluded.fatigue_delta_sum,
                "unsubscribe_risk_sum": MetricsSummary.unsubscribe_risk_sum + excluded.unsubscribe_risk_sum,
                "unsubscribe_risk_delta_sum": (
                    MetricsSummary.unsubscribe_risk_delta_sum + excluded.unsubscribe_risk_delta_sum
                ),
                "assignments": excluded.assignments,
                "updated_at": func.now(),
            },
        )
    )


def _fallback_upsert_metrics_summary(db: Session, values: dict) -> None:
    existing = db.get(MetricsSummary, values["policy"])
    if existing is None:
        db.add(MetricsSummary(**values))
        return
    existing.event_count += values["event_count"]
    existing.cumulative_reward += values["cumulative_reward"]
    existing.cumulative_long_term_reward += values["cumulative_long_term_reward"]
    existing.fatigue_delta_sum += values["fatigue_delta_sum"]
    existing.unsubscribe_risk_sum += values["unsubscribe_risk_sum"]
    existing.unsubscribe_risk_delta_sum += values["unsubscribe_risk_delta_sum"]
    existing.assignments = values["assignments"]


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
