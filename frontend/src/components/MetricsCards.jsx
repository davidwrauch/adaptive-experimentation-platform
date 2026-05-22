import React from "react";
import { HelpLabel } from "./InfoTooltip";
import { formatPolicyLabel, policyPerformanceInsight } from "../interpretations";

export default function MetricsCards({ metrics, uplift, liveMode = false, liveTick = {}, lastUpdated = null }) {
  const totalReward = metrics.policies.reduce(
    (sum, policy) => sum + policy.cumulative_reward,
    0,
  );
  const bestPolicy = [...metrics.policies].sort(
    (a, b) => b.average_reward - a.average_reward,
  )[0];
  const bestLongTermPolicy = [...metrics.policies].sort(
    (a, b) =>
      (b.behavioral?.average_long_term_reward ?? b.average_reward) -
      (a.behavioral?.average_long_term_reward ?? a.average_reward),
  )[0];
  const healthScore = metrics.observability?.health_score ?? 100;
  const rollback = metrics.rollout?.rollback?.recommendation ?? "continue";

  return (
    <section className="summary-band" aria-label="Summary metrics">
      <div className="panel-note">
        These cards summarize replayed production-style traffic: total logged events,
        live status, current winners, health, and rollback posture.
      </div>
      <div className="metrics-grid">
        <div className="metric-card">
          <HelpLabel help="What: total logged assignment/outcome events. Why: more events usually improve confidence. Good: growing steadily. Bad: sudden drops. Action: check ingestion or live simulation.">
            Event count
          </HelpLabel>
          <strong>{metrics.total_events.toLocaleString()}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: whether browser-driven simulation is actively appending events. Why: shows if the demo is behaving like live traffic. Good: running with steady ticks. Bad: paused or backend warming. Action: start live mode or refresh details.">
            Live status
          </HelpLabel>
          <strong className={liveMode ? "live-text" : ""}>{liveMode ? "Live" : "Paused"}</strong>
          <small>{liveTick.event_count_added ?? 0} events added last tick</small>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: policy with highest average immediate reward. Why: identifies short-term winner. Good: winner also looks safe long-term. Bad: winner drives fatigue. Action: check governance before rollout.">
            Best immediate policy
          </HelpLabel>
          <strong className="policy-label">{formatPolicyLabel(bestPolicy?.policy)}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: policy with strongest average long-term reward. Why: indicates retention-aware value after fatigue and unsubscribe risk. Good: aligned with business retention goals. Bad: differs sharply from immediate winner. Action: investigate the tradeoff.">
            Best long-term policy
          </HelpLabel>
          <strong className="policy-label">{formatPolicyLabel(bestLongTermPolicy?.policy)}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: aggregate experiment observability score. Why: summarizes traffic quality, drift, overlap, volume, and risk exposure. Good: 80 or higher. Bad: warnings or critical alerts. Action: slow rollout or review alerts.">
            Health score
          </HelpLabel>
          <strong>{healthScore}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: rollback posture from rollout and observability checks. Why: gives operators a fast safety read. Good: continue. Bad: rollback or review. Action: pause exposure and inspect alerts.">
            Rollback recommendation
          </HelpLabel>
          <strong>{rollback}</strong>
          <small>Updated {formatUpdated(lastUpdated)}</small>
        </div>
      </div>
      <small>Total immediate reward: {totalReward.toFixed(0)}</small>
      {uplift?.incremental_value_winner && (
        <small>Incrementality winner: {formatPolicyLabel(uplift.incremental_value_winner)}</small>
      )}
      <div className="interpretation-card">{policyPerformanceInsight(metrics)}</div>
    </section>
  );
}

function formatUpdated(value) {
  if (!value) {
    return "pending";
  }
  return value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
