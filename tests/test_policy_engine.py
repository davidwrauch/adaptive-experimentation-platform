from app.services.policy_engine import PolicyEngine


def test_policy_engine_supports_required_policies():
    engine = PolicyEngine()
    policies = ["static", "epsilon_greedy", "thompson_sampling", "linucb"]

    for policy in policies:
        action, propensity = engine.choose(policy, context={"engagement": 0.7})

        assert action in {"control", "variant_a", "variant_b"}
        assert 0 < propensity <= 1


def test_policy_engine_updates_rewards():
    engine = PolicyEngine()
    engine.update("epsilon_greedy", "variant_a", 1.0)
    engine.update("epsilon_greedy", "variant_a", 0.0)

    assert engine.counts["epsilon_greedy"]["variant_a"] == 2
    assert engine.rewards["epsilon_greedy"]["variant_a"] == 1.0

