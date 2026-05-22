import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

export default function BayesianPanel({ bayesian }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: beta-binomial reward comparison updated as events arrive. Why: supports sequential decisions without waiting for one fixed end date. Good: high probability best with enough traffic and narrow intervals. Bad: wide uncertainty or review recommendation. Action: continue, expand, stop, or review.">
            Bayesian sequential results
          </HelpLabel>
        </h2>
        <span className="status-pill status-canary">{bayesian?.recommendation ?? "continue"}</span>
      </div>
      <p className="panel-copy">
        A beta-binomial comparison estimates each policy's reward uncertainty and whether the
        experiment should continue, expand, stop, or move to review.
      </p>
      <WhyThisMatters>
        Sequential confidence updating helps teams make staged rollout decisions as evidence
        accumulates, while still preserving uncertainty bands for executive and operator review.
      </WhyThisMatters>
      <div className="probability-grid">
        {(bayesian?.policies ?? []).map((policy) => (
          <article className="probability-card" key={policy.policy}>
            <div>
              <strong>{policy.policy}</strong>
              <small>{policy.event_count} events</small>
            </div>
            <div className="probability-value">{(policy.probability_best * 100).toFixed(1)}%</div>
            <span className="mini-track">
              <span className="mini-fill" style={{ width: `${policy.probability_best * 100}%` }} />
            </span>
            <small>
              mean {policy.posterior_mean.toFixed(4)} | interval{" "}
              {policy.credible_interval[0].toFixed(4)}-{policy.credible_interval[1].toFixed(4)}
            </small>
          </article>
        ))}
      </div>
      <small>{bayesian?.reason}</small>
    </section>
  );
}
