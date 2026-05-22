import React from "react";
import { HelpLabel } from "./InfoTooltip";
import { formatPolicyLabel, launchRecommendation, policyPerformanceInsight } from "../interpretations";

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
  const posture = launchRecommendation(metrics, uplift);

  return (
    <section className="summary-band" aria-label="Summary metrics">
      <div className="metrics-grid">
        <div className="metric-card">
          <HelpLabel help="What: total logged assignment/outcome events. Why: more events usually improve confidence. Good: growing steadily. Bad: sudden drops. Action: check ingestion or live simulation.">
            Traffic
          </HelpLabel>
          <strong>{metrics.total_events.toLocaleString()} events</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: whether browser-driven simulation is actively appending events. Why: shows if the demo is behaving like live traffic. Good: running with steady ticks. Bad: paused or backend warming. Action: start live mode or refresh details.">
            Live status
          </HelpLabel>
          <strong className={liveMode ? "live-text" : ""}>{liveMode ? "Running" : "Paused"}</strong>
          <small>{liveTick.event_count_added ?? 0} events added last tick</small>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: policy with highest average immediate reward. Why: identifies short-term winner. Good: winner also looks safe long-term. Bad: winner drives fatigue. Action: check governance before rollout.">
            Short-term winner
          </HelpLabel>
          <strong className="policy-label">{formatPolicyLabel(bestPolicy?.policy)}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: policy with strongest average long-term reward. Why: indicates retention-aware value after fatigue and unsubscribe risk. Good: aligned with business retention goals. Bad: differs sharply from immediate winner. Action: investigate the tradeoff.">
            Long-term winner
          </HelpLabel>
          <strong className="policy-label">{formatPolicyLabel(bestLongTermPolicy?.policy)}</strong>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: aggregate experiment observability score. Why: summarizes traffic quality, drift, overlap, volume, and risk exposure. Good: 80 or higher. Bad: warnings or critical alerts. Action: slow rollout or review alerts.">
            Health
          </HelpLabel>
          <strong>{healthScore} / 100</strong>
          <small>{healthScore >= 80 ? "Stable" : "Monitor Closely"}</small>
        </div>
        <div className="metric-card">
          <HelpLabel help="What: launch posture from rollout, health, uncertainty, and incrementality checks. Hold Expansion means the system is not calling the experiment a failure. It means the policy should not be expanded until traffic quality, saturation, or risk checks improve. Rollback is reserved for already-expanded policies with severe safety or performance issues.">
            Launch posture
          </HelpLabel>
          <span className={`launch-badge launch-${slug(posture.state)}`}>{posture.state}</span>
          <small>{posture.confidence}</small>
        </div>
      </div>
      <div className="confidence-line">
        <strong>{posture.confidence}</strong>
        <span>Updated {formatUpdated(lastUpdated)}</span>
      </div>
      <div className="overview-scorecard-row">
        <MiniScore label="Experiment result" value={`${formatPolicyLabel(bestPolicy?.policy)} wins short-term response`} />
        <MiniScore label="Long-term result" value={`${formatPolicyLabel(bestLongTermPolicy?.policy)} is stronger on retention`} />
        <MiniScore label="Incrementality winner" value={formatPolicyLabel(uplift?.incremental_value_winner)} />
        <MiniScore label="Operational recommendation" value={`${posture.state} until guardrails are resolved`} />
      </div>
      <small>Total immediate reward: {totalReward.toFixed(0)}</small>
      {uplift?.incremental_value_winner && (
        <small>Incrementality winner: {formatPolicyLabel(uplift.incremental_value_winner)}</small>
      )}
      <div className="interpretation-card compact-callout">{policyPerformanceInsight(metrics)}</div>
    </section>
  );
}

function MiniScore({ label, value }) {
  return (
    <div className="mini-score-card">
      <span>{label}</span>
      <strong className="policy-label">{value ?? "n/a"}</strong>
    </div>
  );
}

function formatUpdated(value) {
  if (!value) {
    return "pending";
  }
  return value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function slug(value) {
  return String(value).toLowerCase().replaceAll(" ", "-");
}
