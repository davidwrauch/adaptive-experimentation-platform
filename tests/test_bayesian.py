from types import SimpleNamespace

from app.services.bayesian import beta_binomial_policy_comparison


def event(policy, reward):
    return SimpleNamespace(policy=policy, reward=reward)


def test_bayesian_comparison_returns_probability_best_and_interval():
    events = [event("a", 1.0) for _ in range(40)] + [event("b", 0.0) for _ in range(40)]

    result = beta_binomial_policy_comparison(events)
    policy_a = next(policy for policy in result["policies"] if policy["policy"] == "a")

    assert policy_a["probability_best"] > 0.5
    assert policy_a["credible_interval"][0] < policy_a["posterior_mean"]
    assert result["recommendation"] in {"continue", "expand", "stop", "review"}


def test_bayesian_recommends_continue_for_small_samples():
    result = beta_binomial_policy_comparison([event("a", 1.0), event("b", 0.0)])

    assert result["recommendation"] == "continue"
