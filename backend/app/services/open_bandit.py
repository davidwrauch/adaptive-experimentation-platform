import csv
from collections.abc import Iterable
from pathlib import Path

from app.services.simulation import (
    build_intervention,
    sample_context,
    simulate_intervention_outcome,
)
import random


COLUMN_ALIASES = {
    "action": ["action", "item_id", "item", "arm", "action_id"],
    "reward": ["reward", "click", "conversion", "outcome"],
    "propensity": ["propensity", "propensity_score", "pscore", "p_score"],
    "logged_policy": ["logged_policy", "policy", "behavior_policy", "campaign"],
    "timestamp": ["timestamp", "time", "datetime", "created_at"],
}


def map_open_bandit_row(row: dict, replay_order: int) -> dict:
    action = str(_first(row, "action", default="unknown_action"))
    reward = float(_first(row, "reward", default=0.0))
    propensity = float(_first(row, "propensity", default=1.0))
    logged_policy = str(_first(row, "logged_policy", default="open_bandit_logged"))
    timestamp = _first(row, "timestamp", default=None)
    context = _context_from_row(row)

    intervention = build_intervention(_normalize_action(action), logged_policy)
    outcome = simulate_intervention_outcome(context, intervention)
    outcome["immediate_reward"] = reward
    outcome["long_term_reward"] = round(
        max(
            0.0,
            min(
                1.0,
                reward * 0.45
                + outcome["delayed_reward"] * 0.35
                + outcome["retention_delta"] * 0.2
                - outcome["fatigue_delta"] * 0.25
                - outcome["unsubscribe_risk_delta"] * 0.35,
            ),
        ),
        4,
    )

    return {
        "user_id": str(row.get("user_id") or row.get("user") or f"obd-user-{replay_order % 1000}"),
        "policy": logged_policy,
        "action": action,
        "reward": reward,
        "propensity": max(0.001, min(1.0, propensity)),
        "context": {
            **context,
            "source": "open_bandit",
            "logged_policy": logged_policy,
            "replay_order": replay_order,
            "timestamp": timestamp,
            "raw_action": action,
            "intervention": intervention,
            "outcome": outcome,
        },
    }


def iter_open_bandit_events(path: str | Path, limit: int | None = None) -> Iterable[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            if limit is not None and index > limit:
                break
            yield map_open_bandit_row(row, replay_order=index)


def _first(row: dict, canonical_name: str, default):
    for key in COLUMN_ALIASES[canonical_name]:
        if key in row and row[key] not in {None, ""}:
            return row[key]
    return default


def _context_from_row(row: dict) -> dict:
    rng = random.Random(str(row))
    context = sample_context(rng)
    for key, value in row.items():
        if key.startswith("user_feature") or key.startswith("context"):
            context[key] = _coerce(value)
    return context


def _coerce(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _normalize_action(action: str) -> str:
    if action in {"control", "variant_a", "variant_b"}:
        return action
    bucket = sum(ord(character) for character in action) % 3
    return ["control", "variant_a", "variant_b"][bucket]
