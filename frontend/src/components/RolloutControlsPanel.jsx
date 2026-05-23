import React, { useEffect, useState } from "react";
import { fetchPolicyControls, pausePolicy, resumePolicy, updatePolicyControl } from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import ResearchPopover from "./ResearchPopover";
import { formatPolicyLabel } from "../interpretations";

export default function RolloutControlsPanel({ rollout, onChanged }) {
  const [controls, setControls] = useState(rollout?.controls ?? []);

  useEffect(() => {
    setControls(rollout?.controls ?? []);
  }, [rollout]);

  async function refreshControls() {
    const body = await fetchPolicyControls();
    setControls(body.policies);
    onChanged?.();
  }

  async function toggle(policy, state) {
    if (state === "paused") {
      await resumePolicy(policy);
    } else {
      await pausePolicy(policy);
    }
    await refreshControls();
  }

  async function saveControl(control) {
    await updatePolicyControl(control.policy, {
      traffic_cap: percentToRatio(control.traffic_cap),
      canary_percentage: percentToRatio(control.canary_percentage),
    });
    await refreshControls();
  }

  function editControl(policy, key, value) {
    setControls((current) =>
      current.map((control) =>
        control.policy === policy ? { ...control, [key]: value } : control,
      ),
    );
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: persisted operating controls for policy exposure. Why: adaptive decisions still need rollout discipline. Good: rollout settings match confidence. Bad: high-risk policy gets too much traffic. Action: pause, lower traffic, or roll back.">
            Rollout controls
          </HelpLabel>
        </h2>
        <span className={`status-pill status-${rollout?.rollback?.recommendation === "rollback" ? "pause" : "canary"}`}>
          {formatRolloutRecommendation(rollout?.rollback?.recommendation)}
        </span>
        <ResearchPopover referenceKey="rollout" />
      </div>
      <p className="panel-copy">
        Use these controls to slow, pause, or safely expand a policy before full deployment.
      </p>
      <WhyThisMatters>
        Rollout controls turn model governance into an operational system: PMs can slow exposure,
        operators can pause risk, and leaders can see why deployment is constrained.
      </WhyThisMatters>
      <div className="control-list">
        {controls.map((control) => (
          <div className="control-row" key={control.policy}>
            <div>
              <strong className="policy-label">{formatPolicyLabel(control.policy)}</strong>
              <span className={`state-badge state-${control.state}`}>
                {control.state === "paused" ? "Paused" : "Active"}
              </span>
            </div>
            <label>
              <HelpLabel help="Maximum share of eligible traffic this policy is allowed to receive.">
                Traffic cap
              </HelpLabel>
              <span className="percentage-value">{formatPercent(control.traffic_cap)}</span>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={ratioToPercent(control.traffic_cap)}
                onChange={(event) => editControl(control.policy, "traffic_cap", event.target.value)}
              />
            </label>
            <label>
              <HelpLabel help="Small initial rollout percentage used to test a policy safely before broader expansion.">
                Canary rollout
              </HelpLabel>
              <span className="percentage-value">{formatPercent(control.canary_percentage)}</span>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={ratioToPercent(control.canary_percentage)}
                onChange={(event) =>
                  editControl(control.policy, "canary_percentage", event.target.value)
                }
              />
            </label>
            <button onClick={() => saveControl(control)}>Save rollout</button>
            <button onClick={() => toggle(control.policy, control.state)}>
              {control.state === "paused" ? "Resume policy" : "Pause policy"}
            </button>
          </div>
        ))}
      </div>
      <small>{rollout?.rollback?.reason}</small>
    </section>
  );
}

function ratioToPercent(value) {
  const numeric = Number(value);
  if (numeric > 1) return Math.round(numeric);
  return Math.round(numeric * 100);
}

function percentToRatio(value) {
  const numeric = Number(value);
  if (numeric > 1) return Number((numeric / 100).toFixed(4));
  return Number(numeric.toFixed(4));
}

function formatPercent(value) {
  return `${ratioToPercent(value)}%`;
}

function formatRolloutRecommendation(value) {
  if (value === "rollback") return "Rollback Recommended";
  if (value === "hold") return "Hold Expansion";
  if (value === "review") return "Human Review Recommended";
  return "Continue Rollout";
}
