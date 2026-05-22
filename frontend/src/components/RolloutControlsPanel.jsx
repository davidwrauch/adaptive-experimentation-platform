import { useEffect, useState } from "react";
import { fetchPolicyControls, pausePolicy, resumePolicy } from "../api";

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

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Rollout controls</h2>
        <span className={`status-pill status-${rollout?.rollback?.recommendation === "rollback" ? "pause" : "canary"}`}>
          {rollout?.rollback?.recommendation ?? "continue"}
        </span>
      </div>
      <p className="panel-copy">
        Traffic caps, canary percentages, and pause states provide an operating layer between
        policy learning and production rollout.
      </p>
      <div className="control-list">
        {controls.map((control) => (
          <div className="control-row" key={control.policy}>
            <strong>{control.policy}</strong>
            <span>cap {(control.traffic_cap * 100).toFixed(0)}%</span>
            <span>canary {(control.canary_percentage * 100).toFixed(0)}%</span>
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
