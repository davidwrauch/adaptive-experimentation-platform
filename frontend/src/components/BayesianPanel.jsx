import React from "react";

export default function BayesianPanel({ bayesian }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Bayesian sequential results</h2>
        <span className="status-pill status-canary">{bayesian?.recommendation ?? "continue"}</span>
      </div>
      <p className="panel-copy">
        A beta-binomial comparison estimates each policy's reward uncertainty and whether the
        experiment should continue, expand, stop, or move to review.
      </p>
      <div className="governance-grid">
        <div className="governance-row governance-head">
          <span>Policy</span>
          <span>Mean</span>
          <span>Best</span>
          <span>Low</span>
          <span>High</span>
          <span>Events</span>
        </div>
        {(bayesian?.policies ?? []).map((policy) => (
          <div className="governance-row" key={policy.policy}>
            <strong>{policy.policy}</strong>
            <span>{policy.posterior_mean.toFixed(4)}</span>
            <span>{(policy.probability_best * 100).toFixed(1)}%</span>
            <span>{policy.credible_interval[0].toFixed(4)}</span>
            <span>{policy.credible_interval[1].toFixed(4)}</span>
            <span>{policy.event_count}</span>
          </div>
        ))}
      </div>
      <small>{bayesian?.reason}</small>
    </section>
  );
}
