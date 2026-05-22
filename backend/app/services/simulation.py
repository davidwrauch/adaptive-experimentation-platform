import random


POLICIES = ["static", "epsilon_greedy", "thompson_sampling", "linucb"]
ACTIONS = ["control", "variant_a", "variant_b"]
CHANNELS = ["email", "sms", "push"]
TONES = ["supportive", "neutral", "urgent"]
TOPIC_FAMILIES = ["education", "benefits", "reminder"]


def sample_context(rng: random.Random) -> dict[str, float]:
    prior_touch_count = rng.randint(0, 18)
    engagement_score = round(rng.uniform(0.15, 0.95), 3)
    fatigue_score = round(min(1.0, 0.08 + prior_touch_count * 0.035 + rng.random() * 0.12), 3)
    profile_maturity = round(rng.choice([0.25, 0.5, 0.75, 1.0]), 2)
    unsubscribe_risk = round(min(0.9, 0.04 + fatigue_score * 0.35), 3)

    return {
        "age_bucket": rng.choice([18, 25, 35, 45, 55]),
        "engagement": engagement_score,
        "prior_sessions": rng.randint(0, 20),
        "engagement_score": engagement_score,
        "fatigue_score": fatigue_score,
        "profile_maturity": profile_maturity,
        "unsubscribe_risk": unsubscribe_risk,
        "prior_touch_count": prior_touch_count,
        "days_since_last_touch": rng.randint(0, 21),
    }


def build_intervention(action: str, policy: str) -> dict[str, str | float | int]:
    action_index = ACTIONS.index(action) if action in ACTIONS else 0
    policy_index = POLICIES.index(policy) if policy in POLICIES else 0
    aggressiveness = {"control": 0.15, "variant_a": 0.45, "variant_b": 0.75}.get(action, 0.35)

    return {
        "channel": CHANNELS[(action_index + policy_index) % len(CHANNELS)],
        "tone": TONES[(action_index * 2 + policy_index) % len(TONES)],
        "cta_aggressiveness": aggressiveness,
        "topic_family": TOPIC_FAMILIES[(action_index + 2 * policy_index) % len(TOPIC_FAMILIES)],
        "message_length": 70 + action_index * 55 + policy_index * 10,
    }


def reward_probability(action: str, context: dict[str, float]) -> float:
    engagement = float(context.get("engagement", 0.5))
    base = {"control": 0.08, "variant_a": 0.12, "variant_b": 0.10}[action]
    lift = 0.10 * engagement if action == "variant_a" else 0.05 * engagement
    return min(0.9, base + lift)


def sample_reward(action: str, context: dict[str, float], rng: random.Random) -> float:
    return 1.0 if rng.random() < reward_probability(action, context) else 0.0


def simulate_intervention_outcome(
    context: dict,
    intervention: dict,
) -> dict[str, float]:
    engagement = float(context.get("engagement_score", context.get("engagement", 0.5)))
    fatigue = float(context.get("fatigue_score", 0.2))
    maturity = float(context.get("profile_maturity", 0.5))
    unsubscribe_risk = float(context.get("unsubscribe_risk", 0.1))
    prior_touch_count = int(context.get("prior_touch_count", 0))
    days_since_last_touch = int(context.get("days_since_last_touch", 7))
    cta = float(intervention.get("cta_aggressiveness", 0.3))
    message_length = int(intervention.get("message_length", 100))

    rest_bonus = min(days_since_last_touch / 30.0, 0.4)
    saturation_penalty = min(prior_touch_count * 0.012, 0.25)
    length_penalty = max(0.0, (message_length - 120) / 500.0)

    immediate_reward = _clamp(
        0.05 + engagement * 0.45 + maturity * 0.12 + cta * 0.10 - fatigue * 0.18 - length_penalty
    )
    fatigue_delta = _clamp(0.015 + cta * 0.08 + max(0, message_length - 100) / 1000 - rest_bonus * 0.03, -1, 1)
    unsubscribe_risk_delta = _clamp(0.004 + cta * 0.04 + fatigue * 0.05 - maturity * 0.015, -1, 1)
    retention_delta = _clamp(0.035 + engagement * 0.08 + maturity * 0.04 - fatigue_delta * 0.7 - unsubscribe_risk * 0.1, -1, 1)
    delayed_reward = _clamp(0.04 + retention_delta + rest_bonus * 0.05 - saturation_penalty - unsubscribe_risk_delta)
    long_term_reward = _clamp(
        immediate_reward * 0.45 + delayed_reward * 0.35 + retention_delta * 0.20 - fatigue_delta * 0.25 - unsubscribe_risk_delta * 0.35,
        -1,
        1,
    )

    return {
        "immediate_reward": round(immediate_reward, 4),
        "delayed_reward": round(delayed_reward, 4),
        "fatigue_delta": round(fatigue_delta, 4),
        "retention_delta": round(retention_delta, 4),
        "unsubscribe_risk_delta": round(unsubscribe_risk_delta, 4),
        "long_term_reward": round(long_term_reward, 4),
    }


def segment_for_context(context: dict) -> str:
    maturity = float(context.get("profile_maturity", 0.5))
    fatigue = float(context.get("fatigue_score", 0.0))
    if fatigue >= 0.65:
        return "high_fatigue"
    if maturity >= 0.75:
        return "mature_profile"
    return "developing_profile"


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))
