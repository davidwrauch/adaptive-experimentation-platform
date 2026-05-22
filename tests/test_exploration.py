from types import SimpleNamespace

from app.services.exploration import exploration_budget_for_context, exploration_saturation_metrics


def test_exploration_increases_under_uncertainty():
    low = exploration_budget_for_context({"profile_maturity": 0.3, "fatigue_score": 0.1}, uncertainty=0.0)
    high = exploration_budget_for_context({"profile_maturity": 0.3, "fatigue_score": 0.1}, uncertainty=0.9)

    assert high["budget"] > low["budget"]


def test_exploration_reduces_for_high_risk_users():
    safe = exploration_budget_for_context({"profile_maturity": 0.9, "unsubscribe_risk": 0.05}, uncertainty=0.8)
    risky = exploration_budget_for_context(
        {"profile_maturity": 0.9, "unsubscribe_risk": 0.5, "fatigue_score": 0.8},
        uncertainty=0.8,
    )

    assert risky["budget"] < safe["budget"]
    assert risky["risk_adjusted"] is True


def test_exploration_saturation_metrics_flags_overuse():
    events = [
        SimpleNamespace(policy="epsilon_greedy", context={"profile_maturity": 0.9, "fatigue_score": 0.1})
        for _ in range(10)
    ]

    metrics = exploration_saturation_metrics(events)

    assert metrics["segments"][0]["saturated"] is True
