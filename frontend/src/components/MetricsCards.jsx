import React from "react";
import { HelpLabel } from "./InfoTooltip";
import { policyPerformanceInsight } from "../interpretations";

export default function MetricsCards({ metrics }) {
  const totalReward = metrics.policies.reduce(
    (sum, policy) => sum + policy.cumulative_reward,
    0,
  );
  const bestPolicy = [...metrics.policies].sort(
    (a, b) => b.average_reward - a.average_reward,
  )[0];

  return (
    <section aria-label="Summary metrics">
      <div className="panel-note">
        These cards summarize replayed production-style traffic: total logged events,
        immediate reward collected, and the current short-term winner.
      </div>
      <div className="metrics-grid">
        <div className="metric-card">
          <HelpLabel help="What: total logged assignment/outcome events. Why: more events usually improve confidence. Good: growing steadily. Bad: sudden drops. Action: check ingestion or live simulation.">
            Event count
          </HelpLabel>
          <strong>{metrics.total_events.toLocaleString()}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: click-like reward collected by policies. Why: measures short-term response. Good: rising without risk spikes. Bad: high clicks paired with fatigue or churn risk. Action: compare against long-term reward.">
            Immediate reward
          </HelpLabel>
          <strong>{totalReward.toFixed(0)}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: policy with highest average immediate reward. Why: identifies short-term winner. Good: winner also looks safe long-term. Bad: winner drives fatigue. Action: check governance before rollout.">
            Best immediate policy
          </HelpLabel>
          <strong>{bestPolicy ? bestPolicy.policy : "n/a"}</strong>
        </div>
      </div>
      <div className="interpretation-card">{policyPerformanceInsight(metrics)}</div>
    </section>
  );
}
