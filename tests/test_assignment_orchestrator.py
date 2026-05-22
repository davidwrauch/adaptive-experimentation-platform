from types import SimpleNamespace

from app.services.assignment_orchestrator import recommend_assignment
from app.services.evidence_retrieval import retrieve_evidence


def event(
    policy="linucb",
    action="variant_a",
    reward=0.3,
    event_id=1,
    long_term_reward=0.32,
    segment_context=None,
):
    context = {
        "engagement_score": 0.7,
        "fatigue_score": 0.2,
        "profile_maturity": 0.9,
        "unsubscribe_risk": 0.08,
        "prior_touch_count": 4,
        "days_since_last_touch": 8,
        "intervention": {
            "channel": "email",
            "tone": "supportive",
            "cta_aggressiveness": 0.25,
            "topic_family": "education",
            "message_length": 80,
        },
        "outcome": {"long_term_reward": long_term_reward},
    }
    if segment_context:
        context.update(segment_context)
    return SimpleNamespace(
        id=event_id,
        policy=policy,
        action=action,
        reward=reward,
        propensity=0.5,
        context=context,
    )


def mature_low_risk_context():
    return {
        "engagement": 0.7,
        "engagement_score": 0.7,
        "fatigue_score": 0.2,
        "profile_maturity": 0.9,
        "unsubscribe_risk": 0.08,
        "prior_touch_count": 5,
        "days_since_last_touch": 9,
    }


def evidence_events(count=60):
    return [event(event_id=i) for i in range(1, count + 1)]


def test_retrieval_returns_required_evidence_sections():
    evidence = retrieve_evidence(evidence_events(3), mature_low_risk_context(), "linucb")

    assert "similar_user_segment_summary" in evidence
    assert "historical_policy_performance" in evidence
    assert "prior_successful_intervention_attributes" in evidence
    assert "current_user_risk_profile" in evidence
    assert evidence["approved_message_templates"]


def test_cold_start_routes_to_deterministic_baseline():
    recommendation = recommend_assignment(
        events=evidence_events(),
        user_context={**mature_low_risk_context(), "profile_maturity": 0.25, "prior_touch_count": 0},
    )

    assert recommendation.route == "cold_start"
    assert recommendation.selected_policy == "linucb"
    assert recommendation.selected_intervention["action"] == "control"


def test_mature_low_risk_routes_to_ai_assisted():
    recommendation = recommend_assignment(
        events=evidence_events(),
        user_context=mature_low_risk_context(),
    )

    assert recommendation.route == "AI_assisted"
    assert recommendation.confidence > 0.5


def test_high_uncertainty_routes_to_human_review():
    recommendation = recommend_assignment(
        events=[event(event_id=1)],
        user_context=mature_low_risk_context(),
    )

    assert recommendation.route == "human_review"
    assert recommendation.governance_reason == "high assignment uncertainty"


def test_high_unsubscribe_risk_routes_to_abstain():
    recommendation = recommend_assignment(
        events=evidence_events(),
        user_context={**mature_low_risk_context(), "unsubscribe_risk": 0.45},
    )

    assert recommendation.route == "abstain"
    assert recommendation.selected_intervention["action"] == "no_send"
