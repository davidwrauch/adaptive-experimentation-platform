import React, { useEffect, useState } from "react";
import { fetchPolicyControls, pausePolicy, resumePolicy, updatePolicyControl } from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

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
      traffic_cap: Number(control.traffic_cap),
      canary_percentage: Number(control.canary_percentage),
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
          <HelpLabel help="What: persisted operating controls for policy exposure. Why: adaptive decisions still need rollout discipline. Good: canaries and caps match confidence. Bad: high-risk policy gets too much traffic. Action: pause, lower cap, or roll back.">
            Rollout controls
          </HelpLabel>
        </h2>
        <span className={`status-pill status-${rollout?.rollback?.recommendation === "rollback" ? "pause" : "canary"}`}>
          {rollout?.rollback?.recommendation ?? "continue"}
        </span>
      </div>
      <p className="panel-copy">
        Traffic caps, canary percentages, and pause states provide an operating layer between
        policy learning and production rollout.
      </p>
      <WhyThisMatters>
        Rollout controls turn model governance into an operational system: PMs can slow exposure,
        operators can pause risk, and leaders can see why deployment is constrained.
      </WhyThisMatters>
      <div className="control-list">
        {controls.map((control) => (
          <div className="control-row" key={control.policy}>
            <strong>{control.policy}</strong>
            <label>
              cap
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={control.traffic_cap}
                onChange={(event) => editControl(control.policy, "traffic_cap", event.target.value)}
              />
            </label>
            <label>
              canary
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={control.canary_percentage}
                onChange={(event) =>
                  editControl(control.policy, "canary_percentage", event.target.value)
                }
              />
            </label>
            <button onClick={() => saveControl(control)}>Save</button>
            <button onClick={() => toggle(control.policy, control.state)}>
              {control.state === "paused" ? "Resume" : "Pause"}
            </button>
          </div>
        ))}
      </div>
      <small>{rollout?.rollback?.reason}</small>
    </section>
  );
}
