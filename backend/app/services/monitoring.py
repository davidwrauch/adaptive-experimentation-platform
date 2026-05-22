from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class MonitoringCheck:
    name: str
    severity: str
    passed: bool
    value: float
    threshold: float
    explanation: str
    recommended_action: str


def run_observability_checks(events: list) -> dict:
    checks = [
        check_sample_ratio_mismatch(events),
        check_traffic_imbalance(events),
        check_event_volume_drop(events),
        check_delayed_reward_gap(events),
        check_low_propensity_overlap(events),
        check_reward_drift(events),
        check_policy_saturation(events),
        check_high_unsubscribe_risk_exposure(events),
    ]
    alerts = [check for check in checks if not check.passed]
    penalty = sum(_severity_penalty(check.severity) for check in alerts)
    health_score = max(0, 100 - penalty)
    return {
        "alerts": [check.__dict__ for check in alerts],
        "health_score": health_score,
        "checks": [check.__dict__ for check in checks],
    }


def check_sample_ratio_mismatch(events: list) -> MonitoringCheck:
    shares = _policy_shares(events)
    value = max(abs(share - (1 / len(shares))) for share in shares.values()) if shares else 0.0
    return _check(
        "sample_ratio_mismatch",
        value <= 0.2,
        value,
        0.2,
        "Policy traffic differs from the expected even allocation.",
        "Inspect assignment logic and replay configuration for policy sampling bias.",
        "warning",
    )


def check_traffic_imbalance(events: list) -> MonitoringCheck:
    shares = _policy_shares(events)
    value = (max(shares.values()) - min(shares.values())) if len(shares) > 1 else 0.0
    return _check(
        "traffic_imbalance",
        value <= 0.35,
        value,
        0.35,
        "One policy is receiving much more traffic than another.",
        "Rebalance routing weights before comparing policy outcomes.",
        "warning",
    )


def check_event_volume_drop(events: list) -> MonitoringCheck:
    counts = _policy_counts(events)
    average = len(events) / len(counts) if counts else 0.0
    value = min(counts.values()) / average if average else 1.0
    return _check(
        "event_volume_drop",
        value >= 0.5,
        value,
        0.5,
        "A policy has less than half the average event volume.",
        "Check ingestion, filters, and assignment traffic for the affected policy.",
        "critical",
    )


def check_delayed_reward_gap(events: list) -> MonitoringCheck:
    gaps = [
        event.reward - float((event.context or {}).get("outcome", {}).get("long_term_reward", event.reward))
        for event in events
    ]
    value = sum(gaps) / len(gaps) if gaps else 0.0
    return _check(
        "delayed_reward_gap",
        value <= 0.2,
        value,
        0.2,
        "Immediate reward is materially higher than long-term reward.",
        "Reduce aggressive interventions and review retention-sensitive segments.",
        "warning",
    )


def check_low_propensity_overlap(events: list) -> MonitoringCheck:
    if not events:
        value = 0.0
    else:
        value = sum(1 for event in events if float(event.propensity) < 0.05) / len(events)
    return _check(
        "low_propensity_overlap",
        value <= 0.15,
        value,
        0.15,
        "Too many events have very low behavior propensities.",
        "Increase exploration or pause OPE comparisons for sparse action regions.",
        "critical",
    )


def check_reward_drift(events: list) -> MonitoringCheck:
    ordered = sorted(enumerate(events), key=lambda item: item[1].id or item[0])
    ordered = [event for _, event in ordered]
    if len(ordered) < 6:
        value = 0.0
    else:
        midpoint = len(ordered) // 2
        early = sum(event.reward for event in ordered[:midpoint]) / midpoint
        late = sum(event.reward for event in ordered[midpoint:]) / (len(ordered) - midpoint)
        value = abs(late - early)
    return _check(
        "reward_drift",
        value <= 0.25,
        value,
        0.25,
        "Observed reward changed substantially between early and recent events.",
        "Compare segment mix and intervention attributes before trusting trend reads.",
        "warning",
    )


def check_policy_saturation(events: list) -> MonitoringCheck:
    policy_touch_counts: dict[str, list[float]] = defaultdict(list)
    for event in events:
        context = event.context or {}
        policy_touch_counts[event.policy].append(float(context.get("prior_touch_count", 0)))

    averages = [
        sum(touch_counts) / len(touch_counts)
        for touch_counts in policy_touch_counts.values()
        if touch_counts
    ]
    value = max(averages) if averages else 0.0
    return _check(
        "policy_saturation",
        value <= 12.0,
        value,
        12.0,
        "A policy is concentrating exposure on heavily touched users.",
        "Throttle repeat exposure and expand eligible low-touch users.",
        "warning",
    )


def check_high_unsubscribe_risk_exposure(events: list) -> MonitoringCheck:
    if not events:
        value = 0.0
    else:
        high_risk = 0
        for event in events:
            context = event.context or {}
            outcome = context.get("outcome", {})
            risk = float(context.get("unsubscribe_risk", 0.0)) + float(
                outcome.get("unsubscribe_risk_delta", 0.0)
            )
            high_risk += int(risk >= 0.35)
        value = high_risk / len(events)
    return _check(
        "high_unsubscribe_risk_exposure",
        value <= 0.2,
        value,
        0.2,
        "A large share of traffic is reaching high unsubscribe-risk users.",
        "Route high-risk users to lower-pressure channels and softer CTAs.",
        "critical",
    )


def _policy_counts(events: list) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for event in events:
        counts[event.policy] += 1
    return dict(counts)


def _policy_shares(events: list) -> dict[str, float]:
    counts = _policy_counts(events)
    total = sum(counts.values())
    if not total:
        return {}
    return {policy: count / total for policy, count in counts.items()}


def _check(
    name: str,
    passed: bool,
    value: float,
    threshold: float,
    explanation: str,
    recommended_action: str,
    failing_severity: str,
) -> MonitoringCheck:
    return MonitoringCheck(
        name=name,
        severity="ok" if passed else failing_severity,
        passed=passed,
        value=round(value, 4),
        threshold=threshold,
        explanation=explanation,
        recommended_action=recommended_action,
    )


def _severity_penalty(severity: str) -> int:
    return {"critical": 20, "warning": 10}.get(severity, 0)
