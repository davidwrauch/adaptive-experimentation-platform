from collections import defaultdict

from app.services.simulation import segment_for_context


BASE_BUDGETS = {
    "developing_profile": 0.25,
    "mature_profile": 0.15,
    "high_fatigue": 0.05,
}


def exploration_budget_for_context(context: dict, uncertainty: float) -> dict:
    segment = segment_for_context(context)
    risk = float(context.get("unsubscribe_risk", 0.0))
    fatigue = float(context.get("fatigue_score", 0.0))
    budget = BASE_BUDGETS.get(segment, 0.1)
    budget += min(0.2, max(0.0, uncertainty) * 0.2)
    if risk >= 0.35 or fatigue >= 0.75:
        budget *= 0.25
    elif risk >= 0.18 or fatigue >= 0.5:
        budget *= 0.6
    return {
        "segment": segment,
        "budget": round(max(0.0, min(0.5, budget)), 4),
        "risk_adjusted": risk >= 0.18 or fatigue >= 0.5,
    }


def exploration_saturation_metrics(events: list) -> dict:
    totals: dict[str, int] = defaultdict(int)
    exploratory: dict[str, int] = defaultdict(int)
    for event in events:
        segment = segment_for_context(event.context or {})
        totals[segment] += 1
        if event.policy in {"epsilon_greedy", "thompson_sampling"}:
            exploratory[segment] += 1

    segments = []
    for segment in sorted(totals):
        observed = exploratory[segment] / totals[segment]
        budget = BASE_BUDGETS.get(segment, 0.1)
        segments.append(
            {
                "segment": segment,
                "event_count": totals[segment],
                "observed_exploration_share": round(observed, 4),
                "budget": budget,
                "saturated": observed > budget * 1.5,
            }
        )
    return {"segments": segments}
