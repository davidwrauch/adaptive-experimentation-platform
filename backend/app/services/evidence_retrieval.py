from collections import Counter, defaultdict

from app.services.simulation import segment_for_context


APPROVED_MESSAGE_TEMPLATES = [
    {
        "template_id": "supportive_email_short",
        "channel": "email",
        "tone": "supportive",
        "cta_aggressiveness": 0.2,
        "topic_family": "education",
        "message_length": 80,
    },
    {
        "template_id": "neutral_push_reminder",
        "channel": "push",
        "tone": "neutral",
        "cta_aggressiveness": 0.35,
        "topic_family": "reminder",
        "message_length": 70,
    },
    {
        "template_id": "supportive_sms_benefits",
        "channel": "sms",
        "tone": "supportive",
        "cta_aggressiveness": 0.25,
        "topic_family": "benefits",
        "message_length": 90,
    },
]


def retrieve_evidence(events: list, user_context: dict, selected_policy: str) -> dict:
    segment = segment_for_context(user_context)
    similar_events = [
        event for event in events if segment_for_context(event.context or {}) == segment
    ]
    policy_events = [event for event in events if event.policy == selected_policy]
    successful_events = [
        event
        for event in events
        if float((event.context or {}).get("outcome", {}).get("long_term_reward", event.reward)) >= 0.25
    ]

    return {
        "similar_user_segment_summary": _segment_summary(segment, similar_events),
        "historical_policy_performance": _policy_summary(selected_policy, policy_events),
        "prior_successful_intervention_attributes": _successful_interventions(successful_events),
        "current_user_risk_profile": _risk_profile(user_context),
        "approved_message_templates": APPROVED_MESSAGE_TEMPLATES,
    }


def summarize_evidence(evidence: dict) -> str:
    segment = evidence["similar_user_segment_summary"]
    policy = evidence["historical_policy_performance"]
    risk = evidence["current_user_risk_profile"]
    return (
        f"{segment['segment']} segment with {segment['event_count']} similar events; "
        f"{policy['policy']} average long-term reward {policy['average_long_term_reward']}; "
        f"risk tier {risk['risk_tier']}."
    )


def _segment_summary(segment: str, events: list) -> dict:
    if not events:
        return {
            "segment": segment,
            "event_count": 0,
            "average_immediate_reward": 0.0,
            "average_long_term_reward": 0.0,
        }
    immediate = sum(event.reward for event in events) / len(events)
    long_term = sum(
        float((event.context or {}).get("outcome", {}).get("long_term_reward", event.reward))
        for event in events
    ) / len(events)
    return {
        "segment": segment,
        "event_count": len(events),
        "average_immediate_reward": round(immediate, 4),
        "average_long_term_reward": round(long_term, 4),
    }


def _policy_summary(policy: str, events: list) -> dict:
    if not events:
        return {
            "policy": policy,
            "event_count": 0,
            "average_reward": 0.0,
            "average_long_term_reward": 0.0,
        }
    return {
        "policy": policy,
        "event_count": len(events),
        "average_reward": round(sum(event.reward for event in events) / len(events), 4),
        "average_long_term_reward": round(
            sum(
                float((event.context or {}).get("outcome", {}).get("long_term_reward", event.reward))
                for event in events
            )
            / len(events),
            4,
        ),
    }


def _successful_interventions(events: list) -> dict:
    if not events:
        return {"event_count": 0, "top_attributes": {}}

    counters: dict[str, Counter] = defaultdict(Counter)
    for event in events:
        intervention = (event.context or {}).get("intervention", {})
        for key in ["channel", "tone", "topic_family"]:
            if key in intervention:
                counters[key][intervention[key]] += 1

    return {
        "event_count": len(events),
        "top_attributes": {
            key: counter.most_common(1)[0][0]
            for key, counter in counters.items()
            if counter
        },
    }


def _risk_profile(context: dict) -> dict:
    unsubscribe_risk = float(context.get("unsubscribe_risk", 0.0))
    fatigue_score = float(context.get("fatigue_score", 0.0))
    if unsubscribe_risk >= 0.35 or fatigue_score >= 0.75:
        tier = "high"
    elif unsubscribe_risk >= 0.18 or fatigue_score >= 0.5:
        tier = "medium"
    else:
        tier = "low"
    return {
        "engagement_score": float(context.get("engagement_score", context.get("engagement", 0.0))),
        "fatigue_score": fatigue_score,
        "profile_maturity": float(context.get("profile_maturity", 0.0)),
        "unsubscribe_risk": unsubscribe_risk,
        "prior_touch_count": int(context.get("prior_touch_count", 0)),
        "days_since_last_touch": int(context.get("days_since_last_touch", 0)),
        "risk_tier": tier,
    }

