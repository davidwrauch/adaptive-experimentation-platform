from types import SimpleNamespace

from app.services.messaging_generation import generate_messaging


def event(policy="linucb", reward=0.3):
    return SimpleNamespace(
        id=1,
        policy=policy,
        action="variant_a",
        reward=reward,
        propensity=0.5,
        context={
            "engagement_score": 0.7,
            "fatigue_score": 0.2,
            "profile_maturity": 0.9,
            "unsubscribe_risk": 0.08,
            "prior_touch_count": 4,
            "days_since_last_touch": 8,
            "intervention": {
                "channel": "email",
                "tone": "supportive",
                "topic_family": "education",
            },
            "outcome": {"long_term_reward": 0.35},
        },
    )


def low_risk_context():
    return {
        "engagement_score": 0.7,
        "fatigue_score": 0.2,
        "profile_maturity": 0.9,
        "unsubscribe_risk": 0.08,
        "prior_touch_count": 4,
        "days_since_last_touch": 8,
    }


def test_deterministic_fallback_generation_includes_variants(monkeypatch):
    monkeypatch.delenv("ENABLE_OPTIONAL_LLM_GENERATION", raising=False)
    generation = generate_messaging([event()], low_risk_context())

    assert generation.candidate_message_variants
    assert generation.cta_variants
    assert generation.cadence_recommendation
    assert generation.message_length_recommendation


def test_retrieved_evidence_is_included():
    generation = generate_messaging([event()], low_risk_context())

    assert generation.retrieved_evidence["similar_segment"]
    assert generation.retrieved_evidence["historical_policy"]
    assert generation.retrieved_evidence["approved_templates"]


def test_human_review_is_always_required():
    generation = generate_messaging([event()], low_risk_context())

    assert generation.requires_human_review is True
    assert all(variant["requires_human_review"] for variant in generation.candidate_message_variants)


def test_high_risk_users_force_abstain_or_review():
    generation = generate_messaging(
        [event()],
        {
            **low_risk_context(),
            "fatigue_score": 0.9,
            "unsubscribe_risk": 0.5,
        },
    )

    assert generation.governance_status == "abstain_or_human_review"
    assert generation.candidate_message_variants[0]["message"].startswith("No outbound")


def test_no_external_api_call_in_tests(monkeypatch):
    monkeypatch.setenv("ENABLE_OPTIONAL_LLM_GENERATION", "true")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    generation = generate_messaging([event()], low_risk_context())

    assert generation.candidate_message_variants
    assert "approved templates" in generation.rationale
