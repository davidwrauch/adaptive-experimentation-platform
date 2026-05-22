from app.services.governance import label_policy
from app.services.ope import OpeEstimate


def ope(
    doubly_robust=0.13,
    uncertainty=0.05,
    effective_sample_size=50,
    low_overlap_risk=False,
):
    return OpeEstimate(
        ips=doubly_robust,
        snips=doubly_robust,
        doubly_robust=doubly_robust,
        uncertainty=uncertainty,
        effective_sample_size=effective_sample_size,
        low_overlap_risk=low_overlap_risk,
    )


def test_governance_deploys_strong_stable_policy():
    decision = label_policy(average_reward=0.14, traffic_share=0.25, ope=ope())

    assert decision.status == "deploy"


def test_governance_canaries_promising_policy():
    decision = label_policy(
        average_reward=0.11,
        traffic_share=0.15,
        ope=ope(doubly_robust=0.11, uncertainty=0.07),
    )

    assert decision.status == "canary"


def test_governance_sends_high_uncertainty_to_review():
    decision = label_policy(
        average_reward=0.13,
        traffic_share=0.2,
        ope=ope(uncertainty=0.2),
    )

    assert decision.status == "human_review"


def test_governance_pauses_low_overlap_policy():
    decision = label_policy(
        average_reward=0.2,
        traffic_share=0.4,
        ope=ope(low_overlap_risk=True),
    )

    assert decision.status == "pause"

