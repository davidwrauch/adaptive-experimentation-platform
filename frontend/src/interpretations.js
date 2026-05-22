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
  const review = policies.some((policy) => policy.governance?.status === "human_review");
  const totalEvents = metrics?.total_events ?? 0;
  const maxTrafficShare = Math.max(0, ...policies.map((policy) => policy.governance?.traffic_share ?? 0));
  const broadExposure = totalEvents >= 75000 || maxTrafficShare >= 0.65;
  const criticalGuardrail = rollback === "rollback" && health < 45;
  const severeLongTermHarm = policies.some(
    (policy) => (policy.behavioral?.average_long_term_reward ?? policy.average_reward ?? 0) < -0.05,
  );
  const highRiskHighTraffic = policies.some(
    (policy) =>
      (policy.behavioral?.average_unsubscribe_risk ?? 0) >= 0.35 &&
      (policy.governance?.traffic_share ?? 0) >= 0.45,
  );

  if (
    (criticalGuardrail && broadExposure) ||
    severeLongTermHarm ||
    highRiskHighTraffic
  ) {
    return {
      state: "Rollback Recommended",
      reason: "Rollback is reserved for already-expanded policies with severe safety or performance issues.",
      score: 25,
      confidence: "Evidence: severe safety issue",
    };
  }
  if (totalEvents < 100) {
    return {
      state: "Hold Expansion",
      reason: "Insufficient confidence: collect more traffic before expanding a policy.",
      score: 45,
      confidence: "Confidence: directional, not launch-ready",
    };
  }
  if (rollback === "rollback") {
    return {
      state: "Hold Expansion",
      reason: "Hold Expansion means the system is not calling the experiment a failure. It means the policy should not be expanded until traffic quality, saturation, or risk checks improve.",
      score: 52,
      confidence: "Evidence: mixed, guardrails active",
    };
  }
  if (health < 75 || uncertain || (metrics?.exploration?.segments ?? []).some((segment) => segment.saturated)) {
    return {
      state: "Hold Expansion",
      reason: "Traffic quality, sample quality, uncertainty, or saturation risk should improve before broader expansion.",
      score: 58,
      confidence: "Confidence: directional, not launch-ready",
    };
  }
  if (review) {
    return {
      state: "Human Review Recommended",
      reason: "At least one policy has a governance review label.",
      score: 55,
      confidence: "Evidence: mixed, guardrails active",
    };
  }
  if (uplift?.average_treatment_effect > 0.05) {
    return {
      state: "Continue Rollout",
      reason: "Incremental value is positive and safety signals are acceptable for controlled rollout.",
      score: 86,
      confidence: "Confidence: positive with active monitoring",
    };
  }
  return {
    state: "Monitor Closely",
    reason: "Evidence is stable, but incremental lift is not yet decisive.",
    score: 74,
    confidence: "Evidence: mixed, guardrails active",
  };
}

export function operationalInsights(metrics, uplift) {
  const insights = [policyPerformanceInsight(metrics), riskInsight(metrics)];
  const rollbackReason = metrics?.rollout?.rollback?.reason;
  if (rollbackReason) {
    insights.push(`Current guardrail posture is driven by: ${rollbackReason}`);
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

export function statisticalPosture(policy, baselinePolicy, bayesianPolicy) {
  const baselineReward = baselinePolicy?.average_reward ?? 0;
  const baselineLongTerm = baselinePolicy?.behavioral?.average_long_term_reward ?? baselineReward;
  const immediateLift = (policy.average_reward ?? 0) - baselineReward;
  const longTermLift = (policy.behavioral?.average_long_term_reward ?? policy.average_reward ?? 0) - baselineLongTerm;
  const probabilityBest = bayesianPolicy?.probability_best ?? 0;
  const uncertainty = policy.ope?.uncertainty ?? 1;
  const eventCount = policy.event_count ?? 0;
  let posture = "Inconclusive";
  let action = "Continue";

  if (eventCount < 50) {
    posture = "Underpowered";
    action = "Hold Expansion";
  } else if (uncertainty >= 0.45) {
    posture = "High Variance";
    action = "Monitor Closely";
  } else if (immediateLift < -0.03 && longTermLift < -0.03) {
    posture = "Likely Negative";
    action = "Rollback Recommended";
  } else if (probabilityBest >= 0.65 && (immediateLift > 0.02 || longTermLift > 0.02)) {
    posture = "Likely Positive";
    action = "Promote";
  } else if (immediateLift > 0 || longTermLift > 0) {
    posture = "Directionally Positive";
    action = policy.governance?.status === "human_review" ? "Human Review" : "Continue";
  }

  if (policy.governance?.status === "pause") {
    action = "Rollback Recommended";
  } else if (policy.governance?.status === "human_review") {
    action = "Human Review";
  }

  return {
    policy: policy.policy,
    immediateLift: round(immediateLift),
    longTermLift: round(longTermLift),
    probabilityBest: round(probabilityBest),
    uncertaintyLevel: uncertainty >= 0.35 ? "High" : uncertainty >= 0.18 ? "Medium" : "Low",
    posture,
    action,
    experimentResult: `${posture}: immediate lift ${round(immediateLift)}, long-term lift ${round(longTermLift)}.`,
    operationalRecommendation: action,
  };
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

export function formatGovernanceStatus(status) {
  return {
    deploy: "Continue Rollout",
    canary: "Monitor Closely",
    human_review: "Human Review",
    pause: "Hold Expansion",
    hold_expansion: "Hold Expansion",
    rollback: "Rollback Recommended",
    review: "Human Review",
    humanReview: "Human Review",
    continue: "Continue Rollout",
  }[status] ?? "Monitor Closely";
}

export function convergenceStatus(metrics) {
  const policies = metrics?.policies ?? [];
  const totalEvents = Math.max(1, metrics?.total_events ?? 0);
  const maxTrafficShare = Math.max(
    0,
    ...policies.map((policy) => (policy.event_count ?? 0) / totalEvents),
  );
  const maxUncertainty = Math.max(0, ...policies.map((policy) => policy.ope?.uncertainty ?? 0));
  const saturated = (metrics?.exploration?.segments ?? []).some((segment) => segment.saturated);
  const driftAlert = (metrics?.observability?.alerts ?? []).some((alert) =>
    String(alert.name).toLowerCase().includes("drift"),
  );
  const criticalAlert = (metrics?.observability?.alerts ?? []).some(
    (alert) => alert.severity === "critical",
  );

  if (criticalAlert) {
    return {
      status: "Needs Review",
      reason: "Critical guardrails are active, so launch owners should review before expansion.",
    };
  }
  if (saturated || maxTrafficShare >= 0.65) {
    return {
      status: "Saturated",
      reason: "Exploration or traffic is concentrated in one segment, policy, or intervention arm.",
    };
  }
  if (driftAlert || maxUncertainty >= 0.4) {
    return {
      status: "Volatile",
      reason: "Reward drift, policy volatility, or high uncertainty suggests recent instability.",
    };
  }
  if (maxUncertainty >= 0.2 || (metrics?.total_events ?? 0) < 1000) {
    return {
      status: "Learning",
      reason: "The system is still collecting evidence and adjusting recommendations.",
    };
  }
  return {
    status: "Stable",
    reason: "Recommendation stability, reward drift, and exploration concentration are within expected bounds.",
  };
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

function round(value) {
  return Number.parseFloat((value ?? 0).toFixed(4));
}
