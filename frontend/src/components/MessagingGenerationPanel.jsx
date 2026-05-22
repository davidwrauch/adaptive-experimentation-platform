import React, { useState } from "react";
import { generateMessaging, sampleUserContext } from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

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
        <h2>
          <HelpLabel help="What: review-only message variants generated from approved evidence. Why: keeps AI assistance bounded by policy and prior campaign context. Good: variants cite evidence and require review. Bad: high-risk profile or unsupported recommendation. Action: human reviewer approves, edits, or rejects.">
            Constrained messaging generation
          </HelpLabel>
        </h2>
        <button onClick={handleGenerate}>{loading ? "Generating..." : "Generate"}</button>
      </div>
      <p className="panel-copy">
        Candidate messages are generated only from approved templates and retrieved evidence.
        Every variant is marked for human review; autonomous deployment is disabled.
      </p>
      <WhyThisMatters>
        Messaging support ties technical decisioning to customer communication quality while
        preserving responsible AI governance and human approval.
      </WhyThisMatters>
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
