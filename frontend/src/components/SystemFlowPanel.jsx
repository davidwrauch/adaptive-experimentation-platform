import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import ResearchPopover from "./ResearchPopover";

const flow = [
  "User context",
  "Candidate interventions",
  "Policy selection",
  "Decision logging",
  "Reward ingestion",
  "Metrics summary",
  "OPE/uplift evaluation",
  "Governance checks",
  "Rollout recommendation",
];

export default function SystemFlowPanel() {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="System Flow shows the operational lifecycle from user context through reward feedback and governance. It is intentionally simple so reviewers can understand the architecture without a diagramming tool.">
            System Flow
          </HelpLabel>
        </h2>
        <ResearchPopover referenceKey="live" />
      </div>
      <p className="panel-copy">
        Northstar decisions move through a logged feedback loop: context creates eligible
        interventions, policies choose actions, outcomes are logged, metrics are updated, and
        governance decides whether traffic can expand.
      </p>
      <WhyThisMatters>
        Real adaptive systems are not just models. They need event lifecycle management, decision
        logging, reward ingestion, continual learning, and governed rollout controls.
      </WhyThisMatters>
      <div className="system-flow">
        {flow.map((step, index) => (
          <React.Fragment key={step}>
            <div className="flow-step">
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </div>
            {index < flow.length - 1 && <div className="flow-arrow">→</div>}
          </React.Fragment>
        ))}
      </div>
    </section>
  );
}
