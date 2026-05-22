import React, { useEffect, useState } from "react";
import { createDecisionRecord, fetchDecisionRecords } from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";
import { formatPolicyLabel } from "../interpretations";

export default function DecisionLogPanel({ metrics }) {
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setError("");
      setRecords(await fetchDecisionRecords(10));
    } catch (err) {
      setError("Decision log is warming up.");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function saveRecommendation() {
    const rollback = metrics.rollout?.rollback ?? {};
    const policy = metrics.policies?.[0]?.policy ?? "unknown";
    await createDecisionRecord({
      decision_type: rollback.recommendation === "rollback" ? "rollback" : "human_review",
      policy,
      evidence_summary: rollback.reason ?? "Saved current governance recommendation.",
      metrics_snapshot: {
        total_events: metrics.total_events,
        health_score: metrics.observability?.health_score,
        rollback,
      },
      operator_reason: "Saved from dashboard for governance audit.",
      system_recommendation: rollback.recommendation ?? "review",
    });
    await refresh();
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: auditable records of deploy, pause, rollback, review, and abstain decisions. Why: accountable AI and experimentation programs need evidence-backed decisions. Good: every major governance action has a record. Bad: undocumented manual overrides. Action: save recommendations before acting.">
            Decision Log
          </HelpLabel>
        </h2>
        <button onClick={saveRecommendation}>Save current recommendation</button>
      </div>
      <WhyThisMatters>
        Decision records connect metrics, operator rationale, and system recommendations so teams
        can explain why an adaptive policy was deployed, paused, rolled back, or sent to review.
      </WhyThisMatters>
      {error && <div className="alert">{error}</div>}
      <div className="event-list">
        {records.map((record) => (
          <article className="event-row" key={record.id}>
            <div>
              <strong>{record.decision_type}</strong>
              <span className="policy-label">{formatPolicyLabel(record.policy)}</span>
            </div>
            <div>
              <span>Signal: {record.system_recommendation}</span>
              <strong>{record.operator_reason || "system recommendation"}</strong>
            </div>
          </article>
        ))}
        {records.length === 0 && <div className="empty-inline">No decision records saved yet.</div>}
      </div>
    </section>
  );
}
