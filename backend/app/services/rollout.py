from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import PolicyControlState
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


def ensure_policy_controls(db: Session) -> None:
    for policy in POLICIES:
        if db.get(PolicyControlState, policy) is None:
            db.add(
                PolicyControlState(
                    policy=policy,
                    traffic_cap=1.0,
                    canary_percentage=0.25,
                    state="active",
                )
            )
    db.commit()


def list_policy_controls(db: Session) -> list[PolicyControl]:
    ensure_policy_controls(db)
    rows = db.query(PolicyControlState).order_by(PolicyControlState.policy).all()
    return [_from_model(row) for row in rows]


def update_policy_control(
    db: Session,
    policy: str,
    traffic_cap: float | None = None,
    canary_percentage: float | None = None,
) -> PolicyControl:
    ensure_policy_controls(db)
    row = _get_or_create(db, policy)
    if traffic_cap is not None:
        row.traffic_cap = _clamp(traffic_cap)
    if canary_percentage is not None:
        row.canary_percentage = _clamp(canary_percentage)
    db.commit()
    db.refresh(row)
    return _from_model(row)


def pause_policy_control(db: Session, policy: str) -> PolicyControl:
    ensure_policy_controls(db)
    row = _get_or_create(db, policy)
    row.state = "paused"
    db.commit()
    db.refresh(row)
    return _from_model(row)


def resume_policy_control(db: Session, policy: str) -> PolicyControl:
    ensure_policy_controls(db)
    row = _get_or_create(db, policy)
    row.state = "active"
    db.commit()
    db.refresh(row)
    return _from_model(row)


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


def _get_or_create(db: Session, policy: str) -> PolicyControlState:
    row = db.get(PolicyControlState, policy)
    if row is None:
        row = PolicyControlState(policy=policy, traffic_cap=1.0, canary_percentage=0.25, state="active")
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def _from_model(row: PolicyControlState) -> PolicyControl:
    return PolicyControl(
        policy=row.policy,
        traffic_cap=row.traffic_cap,
        canary_percentage=row.canary_percentage,
        state=row.state,
    )
