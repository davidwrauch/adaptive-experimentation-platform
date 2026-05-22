from collections import defaultdict
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class OpeEstimate:
    ips: float
    snips: float
    doubly_robust: float
    uncertainty: float
    effective_sample_size: float
    low_overlap_risk: bool


def estimate_policy_value(events: list, target_policy: str) -> OpeEstimate:
    if not events:
        return OpeEstimate(0.0, 0.0, 0.0, 0.0, 0.0, True)

    target_distribution = _target_action_distribution(events, target_policy)
    action_reward_model = _action_reward_model(events)
    weighted_rewards: list[float] = []
    weights: list[float] = []
    dr_terms: list[float] = []

    for event in events:
        target_probability = target_distribution.get(event.action, 0.0)
        behavior_probability = max(float(event.propensity), 0.001)
        weight = target_probability / behavior_probability
        q_value = action_reward_model.get(event.action, 0.0)

        weights.append(weight)
        weighted_rewards.append(weight * event.reward)
        dr_terms.append(q_value + weight * (event.reward - q_value))

    ips = sum(weighted_rewards) / len(events)
    snips = sum(weighted_rewards) / sum(weights) if sum(weights) else 0.0
    doubly_robust = sum(dr_terms) / len(dr_terms)
    uncertainty = _standard_error(dr_terms)
    ess = _effective_sample_size(weights)
    low_overlap_risk = ess < max(5.0, 0.1 * len(events)) or not target_distribution

    return OpeEstimate(
        ips=round(ips, 4),
        snips=round(snips, 4),
        doubly_robust=round(doubly_robust, 4),
        uncertainty=round(uncertainty, 4),
        effective_sample_size=round(ess, 2),
        low_overlap_risk=low_overlap_risk,
    )


def _target_action_distribution(events: list, target_policy: str) -> dict[str, float]:
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        if event.policy == target_policy:
            counts[event.action] += 1

    total = sum(counts.values())
    if not total:
        return {}
    return {action: count / total for action, count in counts.items()}


def _action_reward_model(events: list) -> dict[str, float]:
    rewards: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        rewards[event.action] += event.reward
        counts[event.action] += 1
    return {action: rewards[action] / counts[action] for action in counts}


def _effective_sample_size(weights: list[float]) -> float:
    squared_sum = sum(weight * weight for weight in weights)
    if not squared_sum:
        return 0.0
    return (sum(weights) ** 2) / squared_sum


def _standard_error(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance / len(values))

