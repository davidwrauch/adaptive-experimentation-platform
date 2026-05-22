from app.services.simulation import segment_for_context


CONTROL_POLICIES = {"static", "control"}
MIN_CONTROL_EVENTS = 5


def uplift_metrics(events: list) -> dict:
    if not events:
        return _empty()

    control_events = [event for event in events if _is_control(event)]
    global_control = _mean_reward(control_events) if control_events else _mean_reward(events)
    sparse_control = len(control_events) < MIN_CONTROL_EVENTS
    policy_groups = _group_by(events, lambda event: event.policy)
    segment_groups = _group_by(events, lambda event: segment_for_context(event.context or {}))

    policies = []
    for policy, policy_events in sorted(policy_groups.items()):
        raw_reward = _mean_reward(policy_events)
        control = _control_for_segment_mix(policy_events, control_events, global_control)
        incremental = raw_reward - control
        policies.append(
            {
                "policy": policy,
                "event_count": len(policy_events),
                "raw_average_reward": round(raw_reward, 4),
                "counterfactual_control_reward": round(control, 4),
                "average_treatment_effect": round(incremental, 4),
                "incremental_reward_captured": round(incremental * len(policy_events), 4),
            }
        )

    segments = []
    for segment, segment_events in sorted(segment_groups.items()):
        treatments = [event for event in segment_events if not _is_control(event)]
        segment_controls = [event for event in segment_events if _is_control(event)]
        fallback_control = global_control if len(segment_controls) < MIN_CONTROL_EVENTS else _mean_reward(segment_controls)
        cate = _mean_reward(treatments) - fallback_control if treatments else 0.0
        segments.append(
            {
                "segment": segment,
                "event_count": len(segment_events),
                "control_event_count": len(segment_controls),
                "conditional_treatment_effect": round(cate, 4),
                "fallback_used": len(segment_controls) < MIN_CONTROL_EVENTS,
            }
        )

    curve = _uplift_curve(events, control_events, global_control)
    top_decile_lift = curve[0]["average_uplift"] if curve else 0.0
    winner_raw = max(policies, key=lambda item: item["raw_average_reward"])
    winner_incremental = max(policies, key=lambda item: item["incremental_reward_captured"])

    return {
        "average_treatment_effect": round(
            _mean_reward([event for event in events if not _is_control(event)]) - global_control,
            4,
        ),
        "control_event_count": len(control_events),
        "sparse_control_fallback": sparse_control,
        "policy_incrementality": policies,
        "segment_cate": segments,
        "top_decile_lift": round(top_decile_lift, 4),
        "uplift_curve": curve,
        "recommended_budget_allocation": _budget_allocation(policies, segments),
        "raw_reward_winner": winner_raw["policy"],
        "incremental_value_winner": winner_incremental["policy"],
        "interpretation": (
            f"{winner_raw['policy']} leads raw reward, while "
            f"{winner_incremental['policy']} captures the most estimated incremental value."
        ),
    }


def _empty() -> dict:
    return {
        "average_treatment_effect": 0.0,
        "control_event_count": 0,
        "sparse_control_fallback": True,
        "policy_incrementality": [],
        "segment_cate": [],
        "top_decile_lift": 0.0,
        "uplift_curve": [],
        "recommended_budget_allocation": [],
        "raw_reward_winner": "n/a",
        "incremental_value_winner": "n/a",
        "interpretation": "No uplift evidence is available yet.",
    }


def _is_control(event) -> bool:
    return event.policy in CONTROL_POLICIES or event.action == "control"


def _mean_reward(events: list) -> float:
    return sum(event.reward for event in events) / len(events) if events else 0.0


def _group_by(events: list, key_fn) -> dict:
    groups = {}
    for event in events:
        groups.setdefault(key_fn(event), []).append(event)
    return groups


def _control_for_segment_mix(policy_events: list, control_events: list, global_control: float) -> float:
    if not policy_events:
        return global_control
    by_segment = _group_by(control_events, lambda event: segment_for_context(event.context or {}))
    weighted = 0.0
    for event in policy_events:
        segment = segment_for_context(event.context or {})
        segment_controls = by_segment.get(segment, [])
        weighted += _mean_reward(segment_controls) if len(segment_controls) >= MIN_CONTROL_EVENTS else global_control
    return weighted / len(policy_events)


def _uplift_curve(events: list, control_events: list, global_control: float) -> list[dict]:
    scored = []
    for event in events:
        segment_controls = [
            control
            for control in control_events
            if segment_for_context(control.context or {}) == segment_for_context(event.context or {})
        ]
        control = _mean_reward(segment_controls) if len(segment_controls) >= MIN_CONTROL_EVENTS else global_control
        scored.append({"event": event, "uplift": event.reward - control})
    scored.sort(key=lambda item: item["uplift"], reverse=True)
    if not scored:
        return []
    bucket_size = max(1, len(scored) // 10)
    curve = []
    for index in range(0, len(scored), bucket_size):
        bucket = scored[index : index + bucket_size]
        decile = len(curve) + 1
        curve.append(
            {
                "decile": decile,
                "event_count": len(bucket),
                "average_uplift": round(sum(item["uplift"] for item in bucket) / len(bucket), 4),
            }
        )
        if decile == 10:
            break
    return curve


def _budget_allocation(policies: list[dict], segments: list[dict]) -> list[dict]:
    positive_policies = [policy for policy in policies if policy["average_treatment_effect"] > 0]
    total = sum(policy["average_treatment_effect"] for policy in positive_policies) or 1.0
    best_segment = max(segments, key=lambda item: item["conditional_treatment_effect"], default={"segment": "all"})
    return [
        {
            "policy": policy["policy"],
            "segment": best_segment["segment"],
            "recommended_share": round(policy["average_treatment_effect"] / total, 4),
            "reason": "Allocate more budget where estimated incremental reward is positive.",
        }
        for policy in positive_policies
    ]
