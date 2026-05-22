import random
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models import Event
from app.services.open_bandit import iter_open_bandit_events
from app.services.metrics_summary import update_metrics_summary
from app.services.policy_engine import policy_engine
from app.services.simulation import (
    POLICIES,
    build_intervention,
    sample_context,
    simulate_intervention_outcome,
)
from app.services.streaming import consume_events_to_db, publish_replay_events


def generate_synthetic_events(n: int = 250, seed: int = 7) -> Iterable[dict]:
    rng = random.Random(seed)
    for i in range(n):
        policy = POLICIES[i % len(POLICIES)]
        context = sample_context(rng)
        action, propensity = policy_engine.choose(policy, context=context)
        intervention = build_intervention(action, policy)
        outcome = simulate_intervention_outcome(context, intervention)
        reward = outcome["immediate_reward"]
        enriched_context = {
            **context,
            "intervention": intervention,
            "outcome": outcome,
        }
        policy_engine.update(policy, action, reward)
        yield {
            "user_id": f"user-{rng.randint(1, 80)}",
            "policy": policy,
            "action": action,
            "reward": reward,
            "propensity": propensity,
            "context": enriched_context,
        }


def replay_to_db(
    db: Session,
    n: int = 250,
    seed: int = 7,
    source: str = "synthetic",
    open_bandit_path: str | None = None,
    mode: str = "direct",
) -> int:
    if source == "synthetic":
        event_payloads = list(generate_synthetic_events(n=n, seed=seed))
    elif source == "open_bandit":
        if not open_bandit_path:
            raise ValueError("--open-bandit-path is required when --source open_bandit")
        event_payloads = list(iter_open_bandit_events(open_bandit_path, limit=n))
    else:
        raise ValueError(f"Unknown replay source: {source}")

    if mode == "stream":
        publish_replay_events(event_payloads)
        return consume_events_to_db(db, max_records=len(event_payloads))
    if mode != "direct":
        raise ValueError(f"Unknown replay mode: {mode}")

    events = [Event(**event) for event in event_payloads]
    db.add_all(events)
    update_metrics_summary(db, events)
    db.commit()
    return len(events)
