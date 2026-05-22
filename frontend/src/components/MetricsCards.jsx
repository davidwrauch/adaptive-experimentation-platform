import React from "react";

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
          <span>Event count</span>
          <strong>{metrics.total_events.toLocaleString()}</strong>
        </div>
        <div className="metric-card">
          <span>Immediate reward</span>
          <strong>{totalReward.toFixed(0)}</strong>
        </div>
        <div className="metric-card">
          <span>Best immediate policy</span>
          <strong>{bestPolicy ? bestPolicy.policy : "n/a"}</strong>
        </div>
      </div>
    </section>
  );
}
