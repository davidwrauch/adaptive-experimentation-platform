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
    return `${formatPolicy(longTermWinner.policy)} is sacrificing short-term clicks for stronger long-term retention, while ${formatPolicy(immediateWinner.policy)} is winning the immediate response metric.`;
  }
  return `${formatPolicy(immediateWinner?.policy)} is currently strongest on both immediate and long-term reward. Validate risk and uncertainty before expanding traffic.`;
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
    return `High unsubscribe risk suggests ${formatPolicy(risky.policy)} may be over-targeting fatigued users. Reduce traffic, soften cadence, or route to review.`;
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
    return `${formatPolicy(uncertain.policy)} has high uncertainty because traffic volume is still low or logged propensities have weak overlap. Keep it in canary or human review.`;
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
