import React from "react";
import { formatPolicyLabel, statisticalPosture } from "../interpretations";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import ResearchPopover from "./ResearchPopover";

export default function ExperimentConfidencePanel({ metrics }) {
  const baseline = (metrics.policies ?? []).find((policy) => policy.policy === "static") ?? metrics.policies?.[0];
  const bayesianByPolicy = Object.fromEntries(
    (metrics.bayesian?.policies ?? []).map((policy) => [policy.policy, policy]),
  );
  const rows = (metrics.policies ?? []).map((policy) =>
    statisticalPosture(policy, baseline, bayesianByPolicy[policy.policy]),
  );

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Experiment confidence separates what the data suggests from what operators should do. It combines lift versus Static Control, Bayesian probability, uncertainty, and governance labels.">
            Experiment Confidence
          </HelpLabel>
        </h2>
        <ResearchPopover referenceKey="confidence" />
      </div>
      <WhyThisMatters>
        A policy can look like a winner without enough power, or it can win short-term clicks while
        losing long-term customer value. Confidence posture keeps those cases separate.
      </WhyThisMatters>
      <div className="confidence-grid">
        {rows.map((row) => (
          <article className="confidence-card" key={row.policy}>
            <div className="confidence-card-head">
              <strong className="policy-label">{formatPolicyLabel(row.policy)}</strong>
              <span className={`confidence-badge confidence-${slug(row.posture)}`}>{row.posture}</span>
            </div>
            <div className="compact-grid confidence-metrics">
              <span>Immediate lift</span>
              <strong>{formatLift(row.immediateLift)}</strong>
              <span>Long-term lift</span>
              <strong>{formatLift(row.longTermLift)}</strong>
              <span>Probability best</span>
              <strong>{(row.probabilityBest * 100).toFixed(1)}%</strong>
              <span>Uncertainty</span>
              <strong>{row.uncertaintyLevel}</strong>
            </div>
            <div className="result-recommendation">
              <div>
                <span>Experiment Result</span>
                <strong>{row.experimentResult}</strong>
              </div>
              <div>
                <span>Operational Recommendation</span>
                <strong>{row.operationalRecommendation}</strong>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function formatLift(value) {
  return value > 0 ? `+${value.toFixed(4)}` : value.toFixed(4);
}

function slug(value) {
  return String(value).toLowerCase().replaceAll(" ", "-");
}
