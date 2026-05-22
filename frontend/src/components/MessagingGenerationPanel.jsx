import React, { useState } from "react";
import { generateMessaging, sampleUserContext } from "../api";

export default function MessagingGenerationPanel() {
  const [generation, setGeneration] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleGenerate() {
    try {
      setLoading(true);
      setError("");
      setGeneration(await generateMessaging(sampleUserContext()));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>Constrained messaging generation</h2>
        <button onClick={handleGenerate}>{loading ? "Generating..." : "Generate"}</button>
      </div>
      <p className="panel-copy">
        Candidate messages are generated only from approved templates and retrieved evidence.
        Every variant is marked for human review; autonomous deployment is disabled.
      </p>
      {error && <div className="alert">{error}</div>}
      {generation ? (
        <div className="messaging-grid">
          <div>
            <strong>Retrieved evidence</strong>
            <p>{generation.retrieved_evidence.summary}</p>
            <small>Governance: {generation.governance_status}</small>
            <small>Human review required: {String(generation.requires_human_review)}</small>
          </div>
          <div>
            <strong>Message variants</strong>
            <ul className="plain-list">
              {generation.candidate_message_variants.map((variant) => (
                <li key={variant.template_id}>{variant.message}</li>
              ))}
            </ul>
          </div>
          <div>
            <strong>CTA variants</strong>
            <p>{generation.cta_variants.join(" / ")}</p>
            <strong>Cadence</strong>
            <p>{generation.cadence_recommendation}</p>
            <strong>Length</strong>
            <p>{generation.message_length_recommendation}</p>
          </div>
          <div>
            <strong>Rationale</strong>
            <p>{generation.rationale}</p>
          </div>
        </div>
      ) : (
        <div className="empty-inline">Generate a review-only messaging recommendation.</div>
      )}
    </section>
  );
}
