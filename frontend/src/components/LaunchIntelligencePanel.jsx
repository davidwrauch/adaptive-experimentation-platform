import React from "react";
import { formatPolicyLabel, launchRecommendation, operationalInsights, uncertaintyInsight } from "../interpretations";
import { HelpLabel } from "./InfoTooltip";

export default function LaunchIntelligencePanel({ metrics, uplift, liveTick }) {
  const recommendation = launchRecommendation(metrics, uplift);
  const policies = metrics.policies ?? [];
  const rawWinner = [...policies].sort((a, b) => b.average_reward - a.average_reward)[0];
  const longTermWinner = [...policies].sort(
    (a, b) =>
      (b.behavioral?.average_long_term_reward ?? b.average_reward) -
      (a.behavioral?.average_long_term_reward ?? a.average_reward),
  )[0];
  const governance = metrics.rollout?.rollback?.recommendation ?? "continue";
  const reviews = policies.filter((policy) => policy.governance?.status === "human_review").length;

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Launch intelligence combines reward, uplift, health, uncertainty, rollback posture, and exploration risk into an operator-facing recommendation.">
            Launch Intelligence
          </HelpLabel>
        </h2>
        <span className={`launch-badge launch-${slug(recommendation.state)}`}>{recommendation.state}</span>
      </div>
      <div className="scorecard-grid">
        <Score label="Raw reward winner" value={formatPolicyLabel(rawWinner?.policy)} />
        <Score label="Long-term winner" value={formatPolicyLabel(longTermWinner?.policy)} />
        <Score label="Uplift winner" value={formatPolicyLabel(uplift?.incremental_value_winner)} />
        <Score label="Governance" value={governance} />
        <Score label="Uncertainty" value={uncertaintyInsight(metrics).startsWith("Policy") ? "Stable" : "High uncertainty"} />
        <Score label="Launch recommendation" value={recommendation.state} />
      </div>
      <div className="launch-safety">
        <div>
          <strong>Launch safety</strong>
          <p>{recommendation.reason}</p>
          <span className="mini-track">
            <span className="mini-fill" style={{ width: `${recommendation.score}%` }} />
          </span>
          <small>Uncertainty-adjusted deployment score: {recommendation.score}/100</small>
        </div>
        <div className="compact-grid">
          <span>Exposure quality</span>
          <strong>{metrics.observability?.health_score ?? 100}/100</strong>
          <span>Risk-adjusted posture</span>
          <strong>{recommendation.state}</strong>
          <span>Policy saturation risk</span>
          <strong>{(metrics.exploration?.segments ?? []).some((segment) => segment.saturated) ? "Elevated" : "Controlled"}</strong>
          <span>Blast radius</span>
          <strong>{metrics.total_events > 10000 ? "Portfolio demo scale" : "Limited demo scale"}</strong>
        </div>
      </div>
      <div className="insight-list">
        {operationalInsights(metrics, uplift).map((insight) => (
          <div className="interpretation-card" key={insight}>{insight}</div>
        ))}
      </div>
      <div className="velocity-grid">
        <Score label="Events processed" value={metrics.total_events.toLocaleString()} />
        <Score label="Policies evaluated" value={policies.length} />
        <Score label="Policies promoted" value={policies.filter((policy) => policy.governance?.status === "deploy").length} />
        <Score label="Rollback recommendations" value={governance === "rollback" ? 1 : 0} />
        <Score label="Human review recommendations" value={reviews} />
        <Score label="Live runs started" value={liveTick?.event_count_added ? 1 : 0} />
        <Score label="Avg time-to-decision" value="simulated 2m" />
      </div>
    </section>
  );
}

function Score({ label, value }) {
  return (
    <div className="score-card">
      <span>{label}</span>
      <strong>{value ?? "n/a"}</strong>
    </div>
  );
}

function slug(value) {
  return String(value).toLowerCase().replaceAll(" ", "-");
}
