import React, { useState } from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { formatPolicyLabel } from "../interpretations";

const POLICIES = ["static", "epsilon_greedy", "thompson_sampling", "linucb"];

export default function PolicyDashboard({ metrics, onSimulate }) {
  const [selectedPolicy, setSelectedPolicy] = useState("epsilon_greedy");
  const [simulationResult, setSimulationResult] = useState(null);
  const [simulating, setSimulating] = useState(false);
  const maxReward = Math.max(1, ...metrics.policies.map((policy) => policy.cumulative_reward));
  const totalEvents = Math.max(1, metrics.total_events);

  async function runSimulation() {
    setSimulating(true);
    try {
      const event = await onSimulate(selectedPolicy);
      setSimulationResult({
        eventsAdded: 1,
        policy: selectedPolicy,
        timestamp: event?.created_at ? new Date(event.created_at) : new Date(),
        rewardEffect: event?.reward ?? 0,
      });
    } finally {
      setSimulating(false);
    }
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: policy-level traffic, assignment mix, and cumulative reward. Why: shows which strategy is producing value. Good: reward grows with balanced traffic and acceptable risk. Bad: one policy dominates traffic without enough evidence. Action: compare with governance and long-term metrics before expanding.">
            Policy performance
          </HelpLabel>
        </h2>
        <div className="policy-simulation-control">
          <label>
            Policy
            <select
              value={selectedPolicy}
              onChange={(event) => setSelectedPolicy(event.target.value)}
              disabled={simulating}
            >
              {POLICIES.map((policy) => (
                <option key={policy} value={policy}>
                  {formatPolicyLabel(policy)}
                </option>
              ))}
            </select>
          </label>
          <button onClick={runSimulation} disabled={simulating} type="button">
            {simulating ? "Running..." : "Run policy simulation"}
          </button>
        </div>
      </div>
      <p className="panel-copy">
        Shows how much traffic each policy assigned to each intervention and how much immediate
        reward it collected. This is the short-term view most experimentation dashboards stop at.
      </p>
      <WhyThisMatters>
        Product teams need to see both the business lift and how that lift was generated. A policy
        can win clicks while still creating churn risk or operational instability.
      </WhyThisMatters>
      {simulationResult && (
        <div className="simulation-result" aria-live="polite">
          <span>Events added <strong>{simulationResult.eventsAdded}</strong></span>
          <span>Policy simulated <strong>{formatPolicyLabel(simulationResult.policy)}</strong></span>
          <span>Reward effect <strong>{formatSigned(simulationResult.rewardEffect)}</strong></span>
          <span>Updated <strong>{formatTime(simulationResult.timestamp)}</strong></span>
        </div>
      )}

      <div className="chart-stack">
        {metrics.policies.map((policy) => (
          <div className="policy-chart-card" key={policy.policy}>
            <div>
              <strong className="policy-label">{formatPolicyLabel(policy.policy)}</strong>
              <small>{((policy.event_count / totalEvents) * 100).toFixed(1)}% traffic share</small>
            </div>
            <div className="chart-metric">
              <div className="bar-track tall">
                <div
                  className="bar-fill"
                  style={{ width: `${(policy.cumulative_reward / maxReward) * 100}%` }}
                />
              </div>
              <small>{policy.cumulative_reward.toFixed(2)} cumulative reward</small>
            </div>
            <div className="assignment-chips">{formatAssignments(policy.assignments)}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function formatSigned(value) {
  const numeric = Number(value) || 0;
  return `${numeric >= 0 ? "+" : ""}${numeric.toFixed(2)}`;
}

function formatTime(value) {
  return value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatAssignments(assignments) {
  const text = Object.entries(assignments)
    .map(([action, count]) => `${action}: ${count}`)
    .join(" / ");
  return text || "No assignments yet";
}
