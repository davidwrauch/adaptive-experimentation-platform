from app.services.simulation import (
    build_intervention,
    sample_context,
    segment_for_context,
    simulate_intervention_outcome,
)
import random


def test_sample_context_contains_user_state_features():
    context = sample_context(random.Random(4))

    assert {
        "engagement_score",
        "fatigue_score",
        "profile_maturity",
        "unsubscribe_risk",
        "prior_touch_count",
        "days_since_last_touch",
    }.issubset(context)


def test_intervention_contains_message_attributes():
    intervention = build_intervention("variant_b", "linucb")

    assert {
        "channel",
        "tone",
        "cta_aggressiveness",
        "topic_family",
        "message_length",
    }.issubset(intervention)


def test_aggressive_intervention_increases_fatigue_and_risk():
    context = {
        "engagement_score": 0.6,
        "fatigue_score": 0.2,
        "profile_maturity": 0.75,
        "unsubscribe_risk": 0.08,
        "prior_touch_count": 2,
        "days_since_last_touch": 12,
    }
    soft = {
        "cta_aggressiveness": 0.1,
        "message_length": 80,
    }
    aggressive = {
        "cta_aggressiveness": 0.9,
        "message_length": 180,
    }

    soft_outcome = simulate_intervention_outcome(context, soft)
    aggressive_outcome = simulate_intervention_outcome(context, aggressive)

    assert aggressive_outcome["fatigue_delta"] > soft_outcome["fatigue_delta"]
    assert aggressive_outcome["unsubscribe_risk_delta"] > soft_outcome["unsubscribe_risk_delta"]
    assert aggressive_outcome["long_term_reward"] < soft_outcome["long_term_reward"]


def test_segment_labels_prioritize_high_fatigue():
    assert segment_for_context({"fatigue_score": 0.8, "profile_maturity": 1.0}) == "high_fatigue"
    assert segment_for_context({"fatigue_score": 0.2, "profile_maturity": 1.0}) == "mature_profile"
    assert segment_for_context({"fatigue_score": 0.2, "profile_maturity": 0.25}) == "developing_profile"

