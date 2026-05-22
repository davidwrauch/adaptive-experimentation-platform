from dataclasses import dataclass

from app.services.ope import OpeEstimate


@dataclass(frozen=True)
class GovernanceDecision:
    status: str
    reason: str
    traffic_share: float


def label_policy(
    average_reward: float,
    traffic_share: float,
    ope: OpeEstimate,
) -> GovernanceDecision:
    if ope.low_overlap_risk or ope.effective_sample_size < 5:
        return GovernanceDecision("pause", "low overlap risk", round(traffic_share, 4))

    if average_reward < 0.05 or ope.doubly_robust < 0.05:
        return GovernanceDecision("pause", "reward below floor", round(traffic_share, 4))

    if ope.uncertainty > 0.15:
        return GovernanceDecision("human_review", "high uncertainty", round(traffic_share, 4))

    if traffic_share < 0.1:
        return GovernanceDecision("human_review", "insufficient traffic", round(traffic_share, 4))

    if ope.doubly_robust >= 0.12 and ope.uncertainty <= 0.08 and traffic_share >= 0.2:
        return GovernanceDecision("deploy", "strong reward with stable overlap", round(traffic_share, 4))

    return GovernanceDecision("canary", "promising but still maturing", round(traffic_share, 4))

