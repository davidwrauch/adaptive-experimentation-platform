import os
from dataclasses import dataclass
from itertools import count
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Event
from app.services.demo_seed import build_demo_events
from app.services.metrics_summary import latest_event_timestamp, update_metrics_summary
from app.services.open_bandit import iter_open_bandit_events, map_open_bandit_row


MAX_REPLAY_BATCH_SIZE = 250


@dataclass
class ReplayState:
    running: bool = False
    source: str = "synthetic"
    batch_size: int = 25
    replay_speed_seconds: int = 7
    total_replayed_events: int = 0
    last_batch_added: int = 0
    message: str = "Replay is paused."


replay_state = ReplayState()
_synthetic_counter = count(start=1)
_open_bandit_counter = count(start=1)


def start_replay(db: Session, source: str, batch_size: int, replay_speed_seconds: int) -> ReplayState:
    replay_state.running = True
    replay_state.source = source
    replay_state.batch_size = min(batch_size, MAX_REPLAY_BATCH_SIZE)
    replay_state.replay_speed_seconds = replay_speed_seconds
    events = _next_events(source, replay_state.batch_size)
    db.add_all(events)
    update_metrics_summary(db, events)
    db.commit()
    replay_state.last_batch_added = len(events)
    replay_state.total_replayed_events += len(events)
    replay_state.message = _message(source, len(events))
    return replay_state


def pause_replay() -> ReplayState:
    replay_state.running = False
    replay_state.last_batch_added = 0
    replay_state.message = "Replay is paused."
    return replay_state


def replay_status(db: Session) -> dict:
    return {
        **replay_state.__dict__,
        "latest_timestamp": latest_event_timestamp(db),
    }


def _next_events(source: str, batch_size: int) -> list[Event]:
    if source == "open_bandit":
        return [Event(**payload) for payload in _open_bandit_payloads(batch_size)]

    start = next(_synthetic_counter)
    events = build_demo_events(n=batch_size)
    for offset, event in enumerate(events):
        event.user_id = f"replay-user-{start + offset}"
        event.context = {**(event.context or {}), "source": "synthetic_replay"}
    return events


def _open_bandit_payloads(batch_size: int) -> list[dict]:
    csv_path = os.getenv("OPEN_BANDIT_CSV_PATH")
    if csv_path and Path(csv_path).exists():
        return list(iter_open_bandit_events(csv_path, limit=batch_size))
    return [
        map_open_bandit_row(_sample_open_bandit_row(next(_open_bandit_counter)), replay_order=index)
        for index in range(1, batch_size + 1)
    ]


def _sample_open_bandit_row(index: int) -> dict:
    action = ["sku-a", "sku-b", "sku-c"][index % 3]
    policy = ["random", "bts"][index % 2]
    click = "1" if index % 4 in {0, 1} else "0"
    propensity = "0.25" if policy == "random" else "0.42"
    return {
        "item_id": action,
        "click": click,
        "propensity_score": propensity,
        "behavior_policy": policy,
        "timestamp": f"2020-01-01 00:{index % 60:02d}:00",
        "user_feature_0": str(round(0.2 + (index % 7) * 0.1, 3)),
    }


def _message(source: str, count_added: int) -> str:
    if source == "open_bandit":
        return (
            f"Added {count_added} Open Bandit-style logged recommendation events. "
            "Set OPEN_BANDIT_CSV_PATH to replay a downloaded CSV."
        )
    return f"Added {count_added} deterministic synthetic lifecycle messaging events."
