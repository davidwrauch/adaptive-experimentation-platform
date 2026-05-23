import React from "react";
import { HelpLabel } from "./InfoTooltip";

const policyDescriptions = {
  static: {
    label: "Static A/B Control",
    tag: "Baseline",
    description: "Traditional equal-split experiment used as the baseline comparison.",
  },
  epsilon_greedy: {
    label: "Epsilon Greedy",
    tag: "Adaptive",
    description: "Explores aggressively and quickly shifts toward messages that get short-term engagement.",
  },
  thompson_sampling: {
    label: "Thompson Sampling",
    tag: "Adaptive",
    description: "Balances learning and performance by favoring options that look promising but still have uncertainty.",
  },
  linucb: {
    label: "LinUCB",
    tag: "Adaptive",
    description: "Personalizes message choices using user context and longer-term behavioral patterns.",
  },
};

const policyOrder = ["static", "epsilon_greedy", "thompson_sampling", "linucb"];

export default function ExperimentComparisonPanel() {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="This comparison explains the experiment without requiring bandit or statistics knowledge: what is being tested, how each adaptive policy behaves, and which outcomes matter.">
            What strategies are being tested?
          </HelpLabel>
        </h2>
      </div>
      <p className="panel-copy">
        Northstar is comparing a traditional static A/B baseline against three adaptive policies that learn from traffic over time.
      </p>
      <div className="experiment-grounding-grid">
        {policyOrder.map((policy) => {
          const strategy = policyDescriptions[policy];
          return (
            <article className="experiment-comparison-card" key={policy}>
              <div className="strategy-card-heading">
                <strong className="policy-label">{strategy.label}</strong>
                <span className="strategy-tag">{strategy.tag}</span>
              </div>
              <p>{strategy.description}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
