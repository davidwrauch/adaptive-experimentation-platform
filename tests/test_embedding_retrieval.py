from types import SimpleNamespace

from app.services.assignment_orchestrator import recommend_assignment
from app.services.embedding_retrieval import (
    KeywordEmbeddingModel,
    retrieve_embedding_evidence,
)


def event(policy="linucb", action="variant_a", reward=0.3):
    return SimpleNamespace(
        id=1,
        policy=policy,
        action=action,
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


def context():
    return {
        "engagement_score": 0.7,
        "fatigue_score": 0.2,
        "profile_maturity": 0.9,
        "unsubscribe_risk": 0.08,
        "prior_touch_count": 4,
        "days_since_last_touch": 8,
    }


def test_embedding_retrieval_returns_relevant_evidence():
    evidence = retrieve_embedding_evidence(
        [event()],
        context(),
        "linucb",
        top_k=3,
        embedding_model=KeywordEmbeddingModel(),
    )

    assert evidence
    assert any(item["metadata"]["type"] == "policy_outcome_summary" for item in evidence)


def test_assignment_uses_embedding_evidence_when_model_available():
    recommendation = recommend_assignment(
        [event() for _ in range(60)],
        context(),
        embedding_model=KeywordEmbeddingModel(),
    )

    assert "Retrieved evidence:" in recommendation.evidence_summary


def test_assignment_falls_back_when_embeddings_unavailable():
    recommendation = recommend_assignment(
        [event() for _ in range(60)],
        context(),
        use_embeddings=False,
    )

    assert "Retrieved evidence:" not in recommendation.evidence_summary
    assert recommendation.evidence_summary
