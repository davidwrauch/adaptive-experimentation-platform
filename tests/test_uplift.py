from types import SimpleNamespace

from app.services.uplift import uplift_metrics


def event(policy, reward, segment="mature_profile", action="variant_a"):
    context = {
        "profile_maturity": 0.9 if segment == "mature_profile" else 0.4,
        "fatigue_score": 0.2 if segment != "high_fatigue" else 0.8,
        "unsubscribe_risk": 0.08,
    }
    return SimpleNamespace(policy=policy, reward=reward, action=action, context=context)


def test_uplift_calculates_average_treatment_effect():
    events = [event("static", 0.1, action="control") for _ in range(10)]
    events += [event("linucb", 0.4) for _ in range(10)]

    metrics = uplift_metrics(events)

    assert metrics["average_treatment_effect"] == 0.3
    assert metrics["incremental_value_winner"] == "linucb"


def test_sparse_control_fallback_is_marked():
    events = [event("static", 0.1, action="control")]
    events += [event("linucb", 0.4) for _ in range(10)]

    metrics = uplift_metrics(events)

    assert metrics["sparse_control_fallback"] is True
    assert any(segment["fallback_used"] for segment in metrics["segment_cate"])


def test_segment_cate_estimate_uses_segment_control_when_available():
    events = [event("static", 0.1, "mature_profile", "control") for _ in range(6)]
    events += [event("linucb", 0.5, "mature_profile") for _ in range(6)]
    events += [event("static", 0.2, "developing_profile", "control") for _ in range(6)]
    events += [event("epsilon_greedy", 0.25, "developing_profile") for _ in range(6)]

    metrics = uplift_metrics(events)
    mature = next(segment for segment in metrics["segment_cate"] if segment["segment"] == "mature_profile")

    assert mature["conditional_treatment_effect"] == 0.4
    assert mature["fallback_used"] is False


def test_uplift_curve_is_sorted_by_lift():
    events = [event("static", 0.1, action="control") for _ in range(10)]
    events += [event("linucb", reward) for reward in [0.9, 0.8, 0.6, 0.3, 0.2, 0.1, 0.0, 0.4, 0.5, 0.7]]

    curve = uplift_metrics(events)["uplift_curve"]

    assert curve[0]["average_uplift"] >= curve[-1]["average_uplift"]
