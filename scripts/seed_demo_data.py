import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import Base, SessionLocal, engine
from app.models import Event


DEMO_POLICY_PLAN = {
    "static": {
        "count": 110,
        "action": "control",
        "immediate": 0.18,
        "long_term": 0.16,
        "fatigue_delta": 0.018,
        "unsubscribe_delta": 0.006,
        "propensity": 0.33,
        "cta": 0.15,
    },
    "epsilon_greedy": {
        "count": 145,
        "action": "variant_b",
        "immediate": 0.36,
        "long_term": 0.14,
        "fatigue_delta": 0.105,
        "unsubscribe_delta": 0.055,
        "propensity": 0.18,
        "cta": 0.85,
    },
    "linucb": {
        "count": 125,
        "action": "variant_a",
        "immediate": 0.28,
        "long_term": 0.34,
        "fatigue_delta": 0.034,
        "unsubscribe_delta": 0.012,
        "propensity": 0.42,
        "cta": 0.35,
    },
    "thompson_sampling": {
        "count": 20,
        "action": "variant_a",
        "immediate": 0.24,
        "long_term": 0.24,
        "fatigue_delta": 0.045,
        "unsubscribe_delta": 0.018,
        "propensity": 0.03,
        "cta": 0.45,
    },
}


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    events = build_demo_events()
    with SessionLocal() as db:
        db.add_all(events)
        db.commit()
    print(
        "Seeded lifecycle messaging demo with "
        f"{len(events)} events: epsilon_greedy wins immediate reward, "
        "linucb wins long-term reward, and thompson_sampling is routed to governance review."
    )


def build_demo_events() -> list[Event]:
    events = []
    event_id = 0
    for policy, plan in DEMO_POLICY_PLAN.items():
        for i in range(plan["count"]):
            event_id += 1
            fatigue = _fatigue(policy, i)
            unsubscribe_risk = _unsubscribe_risk(policy, i)
            maturity = 0.9 if policy == "linucb" else 0.65
            context = {
                "age_bucket": [25, 35, 45, 55][i % 4],
                "engagement": round(0.45 + (i % 10) * 0.025, 3),
                "prior_sessions": 3 + (i % 12),
                "engagement_score": round(0.45 + (i % 10) * 0.025, 3),
                "fatigue_score": fatigue,
                "profile_maturity": maturity,
                "unsubscribe_risk": unsubscribe_risk,
                "prior_touch_count": _prior_touch_count(policy, i),
                "days_since_last_touch": 2 + (i % 12),
                "intervention": {
                    "channel": _channel(policy),
                    "tone": _tone(policy),
                    "cta_aggressiveness": plan["cta"],
                    "topic_family": _topic(policy),
                    "message_length": _message_length(policy),
                },
                "outcome": {
                    "immediate_reward": plan["immediate"],
                    "delayed_reward": round(plan["long_term"] * 0.75, 4),
                    "fatigue_delta": plan["fatigue_delta"],
                    "retention_delta": round(plan["long_term"] - plan["fatigue_delta"], 4),
                    "unsubscribe_risk_delta": plan["unsubscribe_delta"],
                    "long_term_reward": plan["long_term"],
                },
            }
            events.append(
                Event(
                    user_id=f"user-{(event_id % 85) + 1}",
                    policy=policy,
                    action=plan["action"],
                    reward=plan["immediate"],
                    propensity=plan["propensity"],
                    context=context,
                )
            )
    return events


def _fatigue(policy: str, index: int) -> float:
    base = {
        "static": 0.28,
        "epsilon_greedy": 0.62,
        "linucb": 0.22,
        "thompson_sampling": 0.38,
    }[policy]
    return round(min(0.92, base + (index % 7) * 0.025), 3)


def _unsubscribe_risk(policy: str, index: int) -> float:
    base = {
        "static": 0.12,
        "epsilon_greedy": 0.28,
        "linucb": 0.08,
        "thompson_sampling": 0.16,
    }[policy]
    return round(min(0.72, base + (index % 6) * 0.025), 3)


def _prior_touch_count(policy: str, index: int) -> int:
    base = {"static": 5, "epsilon_greedy": 13, "linucb": 4, "thompson_sampling": 7}[policy]
    return base + (index % 5)


def _channel(policy: str) -> str:
    return {
        "static": "email",
        "epsilon_greedy": "push",
        "linucb": "email",
        "thompson_sampling": "sms",
    }[policy]


def _tone(policy: str) -> str:
    return "urgent" if policy == "epsilon_greedy" else "supportive"


def _topic(policy: str) -> str:
    return "reminder" if policy == "epsilon_greedy" else "education"


def _message_length(policy: str) -> int:
    return 180 if policy == "epsilon_greedy" else 90


if __name__ == "__main__":
    main()
