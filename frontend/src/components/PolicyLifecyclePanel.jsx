import React, { useEffect, useState } from "react";
import {
  createPolicyVersion,
  fetchPolicyVersions,
  promotePolicyVersion,
  rollbackPolicyVersion,
} from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

export default function PolicyLifecyclePanel() {
  const [versions, setVersions] = useState([]);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setError("");
      setVersions(await fetchPolicyVersions());
    } catch (err) {
      setError("Policy lifecycle registry is warming up.");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function addCandidate() {
    await createPolicyVersion({
      policy_name: "linucb",
      version: `v${versions.length + 1}`,
      status: "candidate",
      rollback_target: "v1",
      notes: "Dashboard-created candidate for demo review.",
    });
    await refresh();
  }

  async function promote(version) {
    await promotePolicyVersion({
      policy_name: version.policy_name,
      version: version.version,
      operator_reason: "Promoted from governance console.",
    });
    await refresh();
  }

  async function rollback(version) {
    await rollbackPolicyVersion({
      policy_name: version.policy_name,
      target_version: version.rollback_target,
      operator_reason: "Rollback requested from governance console.",
    });
    await refresh();
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: champion/challenger lifecycle registry for policy versions. Why: production personalization needs explicit version state and rollback targets. Good: one champion with candidates/challengers. Bad: no rollback target. Action: promote only after evidence and keep rollback ready.">
            Policy Lifecycle
          </HelpLabel>
        </h2>
        <button onClick={addCandidate}>Add candidate</button>
      </div>
      <WhyThisMatters>
        Lifecycle state turns experiments into managed production assets: candidates are reviewed,
        challengers are compared, champions are deployed, and archived versions remain auditable.
      </WhyThisMatters>
      {error && <div className="alert">{error}</div>}
      <div className="governance-grid">
        {(versions.length ? versions : seedRows()).map((version) => (
          <div className="governance-row lifecycle-row" key={`${version.policy_name}-${version.version}`}>
            <strong>{version.policy_name}</strong>
            <span>{version.version}</span>
            <span className={`status-pill status-${statusClass(version.status)}`}>{version.status}</span>
            <span>{version.rollback_target ?? "none"}</span>
            <div className="button-row">
              <button onClick={() => promote(version)}>Promote</button>
              <button onClick={() => rollback(version)}>Rollback</button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function statusClass(status) {
  if (status === "champion") return "deploy";
  if (status === "candidate") return "canary";
  if (status === "challenger") return "human_review";
  return "pause";
}

function seedRows() {
  return [
    { policy_name: "linucb", version: "v1", status: "champion", rollback_target: null },
    { policy_name: "epsilon_greedy", version: "v1", status: "challenger", rollback_target: "v0" },
  ];
}
