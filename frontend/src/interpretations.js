export function policyPerformanceInsight(metrics) {
  const policies = metrics?.policies ?? [];
  if (policies.length === 0) {
    return "No traffic has arrived yet. Start live simulation to build evidence.";
  }

  const immediateWinner = [...policies].sort((a, b) => b.average_reward - a.average_reward)[0];
  const longTermWinner = [...policies].sort(
    (a, b) =>
      (b.behavioral?.average_long_term_reward ?? b.average_reward) -
      (a.behavioral?.average_long_term_reward ?? a.average_reward),
  )[0];

  if (immediateWinner?.policy && longTermWinner?.policy && immediateWinner.policy !== longTermWinner.policy) {
    return `${formatPolicyLabel(longTermWinner.policy)} is sacrificing short-term clicks for stronger long-term retention, while ${formatPolicyLabel(immediateWinner.policy)} is winning the immediate response metric.`;
  }
  return `${formatPolicyLabel(immediateWinner?.policy)} is currently strongest on both immediate and long-term reward. Validate risk and uncertainty before expanding traffic.`;
}

export function formatPolicyLabel(policy) {
  if (!policy || policy === "n/a") {
    return "n/a";
  }
  return {
    static: "Static Control",
    epsilon_greedy: "Epsilon Greedy",
    linucb: "LinUCB",
    thompson_sampling: "Thompson Sampling",
  }[policy] ?? formatPolicy(policy);
}

export function launchRecommendation(metrics, uplift) {
  const rollback = metrics?.rollout?.rollback?.recommendation;
  const health = metrics?.observability?.health_score ?? 100;
  const policies = metrics?.policies ?? [];
  const uncertain = policies.some((policy) => (policy.ope?.uncertainty ?? 0) >= 0.35);
  const totalEvents = metrics?.total_events ?? 0;
  if (rollback === "rollback") {
    return { state: "Rollback Recommended", reason: "Rollback posture is active based on current monitoring or rollout checks.", score: 25 };
  }
  if (totalEvents < 100) {
    return { state: "Insufficient Evidence", reason: "Collect more traffic before promoting a policy.", score: 45 };
  }
  if (health < 75 || uncertain) {
    return { state: "Monitor Closely", reason: "Health or uncertainty signals argue for controlled exposure.", score: 62 };
  }
  if (uplift?.average_treatment_effect > 0.05) {
    return { state: "Promote", reason: "Incremental value is positive and safety signals are acceptable.", score: 86 };
  }
  return { state: "Continue", reason: "Evidence is stable, but incremental lift is not yet decisive.", score: 74 };
}

export function operationalInsights(metrics, uplift) {
  const insights = [policyPerformanceInsight(metrics), riskInsight(metrics)];
  const rollbackReason = metrics?.rollout?.rollback?.reason;
  if (rollbackReason) {
    insights.push(`Current rollback posture is driven by: ${rollbackReason}`);
  }
  if ((uplift?.recommended_budget_allocation ?? []).length > 0) {
    const top = uplift.recommended_budget_allocation[0];
    insights.push(`${formatPolicyLabel(top.policy)} has positive estimated incremental value for ${top.segment}; consider allocating controlled budget there.`);
  }
  const saturated = (metrics?.exploration?.segments ?? []).find((segment) => segment.saturated);
  if (saturated) {
    insights.push(`Exploration is over-concentrated in ${saturated.segment}; reduce exploration pressure for that segment.`);
  }
  return insights.slice(0, 4);
}

export function riskInsight(metrics) {
  const risky = [...(metrics?.policies ?? [])].sort(
    (a, b) =>
      (b.behavioral?.average_unsubscribe_risk ?? 0) -
      (a.behavioral?.average_unsubscribe_risk ?? 0),
  )[0];

  if (!risky) {
    return "Risk is not available until events include behavioral outcomes.";
  }
  if ((risky.behavioral?.average_unsubscribe_risk ?? 0) >= 0.3) {
    return `High unsubscribe risk suggests ${formatPolicyLabel(risky.policy)} may be over-targeting fatigued users. Reduce traffic, soften cadence, or route to review.`;
  }
  return "Unsubscribe risk is stable. Keep monitoring as traffic shifts across segments.";
}

export function uncertaintyInsight(metrics) {
  const uncertain = [...(metrics?.policies ?? [])].sort(
    (a, b) => (b.ope?.uncertainty ?? 0) - (a.ope?.uncertainty ?? 0),
  )[0];

  if (!uncertain) {
    return "Uncertainty will appear once policies have enough logged traffic for comparison.";
  }
  if ((uncertain.ope?.uncertainty ?? 0) >= 0.25 || uncertain.event_count < 100) {
    return `${formatPolicyLabel(uncertain.policy)} has high uncertainty because traffic volume is still low or logged propensities have weak overlap. Keep it in canary or human review.`;
  }
  return "Policy uncertainty is stable enough for cautious rollout decisions.";
}

export function severityInterpretation(status) {
  const copy = {
    stable: {
      interpretation: "Metrics are within expected operating bounds.",
      action: "Continue monitoring and expand only if governance also agrees.",
    },
    warning: {
      interpretation: "A metric is drifting toward a risk threshold.",
      action: "Investigate segments, reduce exposure, or slow rollout.",
    },
    critical: {
      interpretation: "The experiment may be unsafe or statistically unreliable.",
      action: "Pause, roll back, or require human review before more traffic ships.",
    },
    high_uncertainty: {
      interpretation: "The system does not yet have enough reliable evidence.",
      action: "Collect more logged data or keep the policy in canary.",
    },
    under_explored: {
      interpretation: "A segment or policy has too little traffic to compare confidently.",
      action: "Allocate limited safe exploration if user risk is low.",
    },
    over_saturated: {
      interpretation: "A segment is receiving more exploration than its budget allows.",
      action: "Reduce exploration, lower traffic caps, or pause risky variants.",
    },
  };
  return copy[status] ?? copy.stable;
}

export function governanceExplanation(status) {
  return {
    deploy: "Evidence is strong enough for broader rollout, assuming business owners accept the risk.",
    canary: "Promising but not final. Expand slowly while watching reward, fatigue, and overlap.",
    human_review: "The system needs operator judgment before exposure grows.",
    pause: "Risk or data quality is too high. Stop exposure until the issue is understood.",
  }[status] ?? "Governance has not produced a clear launch label yet.";
}

function formatPolicy(policy) {
  if (!policy) {
    return "No policy";
  }
  return policy
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
