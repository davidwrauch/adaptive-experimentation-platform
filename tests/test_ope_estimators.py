from types import SimpleNamespace

from app.services.ope import estimate_policy_value


def event(policy, action, reward, propensity):
    return SimpleNamespace(
        policy=policy,
        action=action,
        reward=reward,
        propensity=propensity,
    )


def test_ips_snips_and_dr_are_deterministic():
    events = [
        event("target", "a", 1.0, 0.5),
        event("target", "b", 0.0, 0.5),
        event("baseline", "a", 1.0, 0.25),
        event("baseline", "b", 1.0, 0.25),
    ]

    estimate = estimate_policy_value(events, "target")

    assert estimate.ips == 1.25
    assert estimate.snips == 0.8333
    assert estimate.doubly_robust == 0.875
    assert estimate.effective_sample_size == 3.6


def test_missing_target_policy_has_low_overlap_risk():
    events = [event("baseline", "a", 1.0, 0.5)]

    estimate = estimate_policy_value(events, "missing")

    assert estimate.ips == 0.0
    assert estimate.low_overlap_risk is True

