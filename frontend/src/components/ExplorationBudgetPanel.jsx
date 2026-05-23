import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import ResearchPopover from "./ResearchPopover";
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
        <ResearchPopover referenceKey="exploration" />
      </div>
      <p className="panel-copy">
        Exploration should increase when uncertainty is high, but shrink for fatigued or
        unsubscribe-risky users. Saturation flags show where exploration may be overused.
      </p>
      <WhyThisMatters>
        Exploration is a business tradeoff: it buys experimentation confidence, but spends user
        attention. Safe systems explore more where risk is low and pull back where fatigue is high.
      </WhyThisMatters>
      <div className="exploration-card-grid">
        {(exploration?.segments ?? []).map((segment) => (
          <article className="exploration-card" key={segment.segment}>
            <div>
              <strong>{segment.segment}</strong>
              <small>{segment.event_count} events</small>
            </div>
            <div>
              <span>Observed {(segment.observed_exploration_share * 100).toFixed(1)}%</span>
              <MiniBar value={segment.observed_exploration_share} max={0.5} />
            </div>
            <div>
              <span>Budget {(segment.budget * 100).toFixed(1)}%</span>
              <MiniBar value={segment.budget} max={0.5} muted />
            </div>
            <small>{segmentStatus(segment.saturated)}</small>
          </article>
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
