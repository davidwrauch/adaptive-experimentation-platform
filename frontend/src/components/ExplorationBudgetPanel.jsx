import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { severityInterpretation } from "../interpretations";

export default function ExplorationBudgetPanel({ exploration }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: compares observed exploration against segment-level budgets. Why: exploration learns faster but can expose users to less-proven choices. Good: low-risk segments explore within budget. Bad: fatigued or risky segments become saturated. Action: reduce exploration or traffic caps.">
            Exploration budget
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Exploration should increase when uncertainty is high, but shrink for fatigued or
        unsubscribe-risky users. Saturation flags show where exploration may be overused.
      </p>
      <WhyThisMatters>
        Exploration is a business tradeoff: it buys experimentation confidence, but spends user
        attention. Safe systems explore more where risk is low and pull back where fatigue is high.
      </WhyThisMatters>
      <div className="risk-grid">
        <div className="risk-row risk-head">
          <span>Segment</span>
          <span>Events</span>
          <span>Observed</span>
          <span>Budget</span>
          <span>Status</span>
        </div>
        {(exploration?.segments ?? []).map((segment) => (
          <div className="risk-row" key={segment.segment}>
            <strong>{segment.segment}</strong>
            <span>{segment.event_count}</span>
            <span>
              {(segment.observed_exploration_share * 100).toFixed(1)}%
              <MiniBar value={segment.observed_exploration_share} max={0.5} />
            </span>
            <span>
              {(segment.budget * 100).toFixed(1)}%
              <MiniBar value={segment.budget} max={0.5} muted />
            </span>
            <span>{segmentStatus(segment.saturated)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function segmentStatus(saturated) {
  const status = saturated ? "over_saturated" : "stable";
  const detail = severityInterpretation(status);
  return `${saturated ? "over-saturated" : "stable"}: ${detail.action}`;
}

function MiniBar({ value, max, muted = false }) {
  return (
    <span className="mini-track">
      <span
        className={muted ? "mini-fill muted" : "mini-fill"}
        style={{ width: `${Math.min(100, (value / max) * 100)}%` }}
      />
    </span>
  );
}
