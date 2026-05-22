from dataclasses import dataclass, field

from app.services.monitoring import run_observability_checks


POLICIES = ["static", "epsilon_greedy", "thompson_sampling", "linucb"]


@dataclass
class PolicyControl:
    policy: str
    traffic_cap: float = 1.0
    canary_percentage: float = 0.25
    state: str = "active"


@dataclass
class RolloutControlStore:
    controls: dict[str, PolicyControl] = field(
        default_factory=lambda: {policy: PolicyControl(policy=policy) for policy in POLICIES}
    )

    def list_controls(self) -> list[PolicyControl]:
        return [self.controls[policy] for policy in sorted(self.controls)]

    def update(self, policy: str, traffic_cap: float | None = None, canary_percentage: float | None = None) -> PolicyControl:
        control = self._get(policy)
        if traffic_cap is not None:
            control.traffic_cap = _clamp(traffic_cap)
        if canary_percentage is not None:
            control.canary_percentage = _clamp(canary_percentage)
        return control

    def pause(self, policy: str) -> PolicyControl:
        control = self._get(policy)
        control.state = "paused"
        return control

    def resume(self, policy: str) -> PolicyControl:
        control = self._get(policy)
        control.state = "active"
        return control

    def get(self, policy: str) -> PolicyControl:
        return self._get(policy)

    def _get(self, policy: str) -> PolicyControl:
        if policy not in self.controls:
            self.controls[policy] = PolicyControl(policy=policy)
        return self.controls[policy]


rollout_store = RolloutControlStore()


def rollout_recommendation(events: list) -> dict:
    observability = run_observability_checks(events)
    critical_alerts = [
        alert for alert in observability["alerts"] if alert["severity"] == "critical"
    ]
    if critical_alerts:
        return {
            "recommendation": "rollback",
            "reason": f"{len(critical_alerts)} critical observability alerts active",
            "affected_checks": [alert["name"] for alert in critical_alerts],
        }
    if observability["alerts"]:
        return {
            "recommendation": "hold",
            "reason": "warning-level observability alerts active",
            "affected_checks": [alert["name"] for alert in observability["alerts"]],
        }
    return {
        "recommendation": "continue",
        "reason": "no severe observability alerts",
        "affected_checks": [],
    }


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)
