from collections import defaultdict


def beta_binomial_policy_comparison(events: list) -> dict:
    stats = _policy_stats(events)
    if not stats:
        return {"policies": [], "recommendation": "continue", "reason": "no events yet"}

    policies = []
    means = {}
    for policy, values in stats.items():
        alpha = 1 + values["successes"]
        beta = 1 + values["failures"]
        mean = alpha / (alpha + beta)
        variance = (alpha * beta) / (((alpha + beta) ** 2) * (alpha + beta + 1))
        band = 1.96 * (variance ** 0.5)
        means[policy] = mean
        policies.append(
            {
                "policy": policy,
                "alpha": alpha,
                "beta": beta,
                "posterior_mean": round(mean, 4),
                "credible_interval": [
                    round(max(0.0, mean - band), 4),
                    round(min(1.0, mean + band), 4),
                ],
                "event_count": values["successes"] + values["failures"],
            }
        )

    total_mean = sum(means.values())
    for policy in policies:
        probability = means[policy["policy"]] / total_mean if total_mean else 0.0
        policy["probability_best"] = round(probability, 4)

    best = max(policies, key=lambda item: item["probability_best"])
    recommendation = _stopping_recommendation(best, policies)
    return {
        "policies": sorted(policies, key=lambda item: item["policy"]),
        **recommendation,
    }


def _policy_stats(events: list) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = defaultdict(lambda: {"successes": 0, "failures": 0})
    for event in events:
        reward = 1 if float(event.reward) >= 0.5 else 0
        stats[event.policy]["successes"] += reward
        stats[event.policy]["failures"] += 1 - reward
    return dict(stats)


def _stopping_recommendation(best: dict, policies: list[dict]) -> dict:
    if best["event_count"] < 30:
        return {"recommendation": "continue", "reason": "insufficient sample size"}
    if best["probability_best"] >= 0.7:
        return {"recommendation": "expand", "reason": f"{best['policy']} has strong posterior support"}
    if any(policy["credible_interval"][1] < 0.08 and policy["event_count"] >= 30 for policy in policies):
        return {"recommendation": "stop", "reason": "at least one policy has persistently weak reward"}
    if best["probability_best"] < 0.4:
        return {"recommendation": "review", "reason": "no clear policy winner"}
    return {"recommendation": "continue", "reason": "collect more evidence before expanding"}
