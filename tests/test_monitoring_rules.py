from types import SimpleNamespace

from app.services.monitoring import (
    check_delayed_reward_gap,
    check_event_volume_drop,
    check_high_unsubscribe_risk_exposure,
    check_low_propensity_overlap,
    check_policy_saturation,
    check_reward_drift,
    check_sample_ratio_mismatch,
    check_traffic_imbalance,
    run_observability_checks,
)


def event(
    policy="a",
    reward=0.1,
    propensity=0.5,
    event_id=1,
    long_term_reward=None,
    prior_touch_count=1,
    unsubscribe_risk=0.05,
    unsubscribe_risk_delta=0.0,
):
    outcome = {
        "long_term_reward": reward if long_term_reward is None else long_term_reward,
        "unsubscribe_risk_delta": unsubscribe_risk_delta,
    }
    return SimpleNamespace(
        id=event_id,
        policy=policy,
        reward=reward,
        propensity=propensity,
        context={
            "prior_touch_count": prior_touch_count,
            "unsubscribe_risk": unsubscribe_risk,
            "outcome": outcome,
        },
    )


def test_sample_ratio_mismatch_rule_flags_policy_skew():
    events = [event("a") for _ in range(9)] + [event("b")]

    check = check_sample_ratio_mismatch(events)

    assert check.passed is False
    assert check.severity == "warning"


def test_traffic_imbalance_rule_flags_large_share_gap():
    events = [event("a") for _ in range(8)] + [event("b") for _ in range(2)]

    check = check_traffic_imbalance(events)

    assert check.passed is False


def test_event_volume_drop_rule_flags_low_volume_policy():
    events = [event("a") for _ in range(10)] + [event("b")]

    check = check_event_volume_drop(events)

    assert check.passed is False
    assert check.severity == "critical"


def test_delayed_reward_gap_rule_flags_short_term_overstatement():
    events = [event(reward=0.8, long_term_reward=0.2) for _ in range(4)]

    check = check_delayed_reward_gap(events)

    assert check.passed is False


def test_low_propensity_overlap_rule_flags_sparse_overlap():
    events = [event(propensity=0.01) for _ in range(3)] + [event(propensity=0.5) for _ in range(7)]

    check = check_low_propensity_overlap(events)

    assert check.passed is False
    assert check.severity == "critical"


def test_reward_drift_rule_flags_early_late_shift():
    early = [event(reward=0.1, event_id=i) for i in range(1, 6)]
    late = [event(reward=0.8, event_id=i) for i in range(6, 11)]

    check = check_reward_drift(early + late)

    assert check.passed is False


def test_policy_saturation_rule_flags_high_repeat_touch_counts():
    events = [event("a", prior_touch_count=15) for _ in range(5)]

    check = check_policy_saturation(events)

    assert check.passed is False


def test_high_unsubscribe_risk_exposure_rule_flags_risky_traffic():
    events = [
        event(unsubscribe_risk=0.4),
        event(unsubscribe_risk=0.45),
        event(unsubscribe_risk=0.05),
        event(unsubscribe_risk=0.08),
    ]

    check = check_high_unsubscribe_risk_exposure(events)

    assert check.passed is False
    assert check.severity == "critical"


def test_observability_summary_returns_alerts_and_health_score():
    events = [event("a", propensity=0.01, unsubscribe_risk=0.5) for _ in range(5)]

    summary = run_observability_checks(events)

    assert summary["alerts"]
    assert summary["health_score"] < 100
    assert len(summary["checks"]) == 8
