import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

const styles = [
  {
    label: "Current winning style",
    value: "Short reminders",
    insight: "Short reminders maximize immediate clicks but increase fatigue risk.",
    confidence: "Directional evidence",
    posture: "Hold Expansion",
  },
  {
    label: "Fatigue-safe style",
    value: "Personalized summaries",
    insight: "Personalized summaries reduce short-term CTR but improve long-term retention.",
    confidence: "Mixed evidence",
    posture: "Monitor Closely",
  },
  {
    label: "Highest incremental style",
    value: "Contextual recommendations",
    insight: "Contextual recommendations show stronger incremental value in mature profiles.",
    confidence: "Directional evidence",
    posture: "Continue Rollout",
  },
];

export default function MessageExperimentationPanel() {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Messaging experiments compare constrained dimensions: length, tone, personalization depth, cadence, urgency level, and intervention category. The system proposes variants from approved templates and evidence; deployment still requires human review.">
            Message experimentation
          </HelpLabel>
        </h2>
        <span className="status-pill status-human_review">Review-only</span>
      </div>
      <p className="panel-copy">
        The AI-assisted layer does not generate arbitrary copy. It combines approved templates,
        tone and length constraints, and retrieval-grounded examples before producing review-only
        candidate variants.
      </p>
      <WhyThisMatters>
        Message quality is part of the experiment. High-frequency interventions show elevated unsubscribe risk
        in low-engagement cohorts, even when they produce attractive short-term
        response rates.
      </WhyThisMatters>

      <div className="message-dimension-strip">
        {["Message length", "Tone", "Personalization depth", "Cadence", "Urgency level", "Intervention category"].map((dimension) => (
          <span key={dimension}>{dimension}</span>
        ))}
      </div>

      <div className="message-style-grid">
        {styles.map((style) => (
          <article className="message-style-card" key={style.label}>
            <div className="label-value-stack">
              <span>{style.label}</span>
              <strong>{style.value}</strong>
            </div>
            <p>{style.insight}</p>
            <small>Confidence: {style.confidence}</small>
            <small>Rollout posture: {style.posture}</small>
          </article>
        ))}
      </div>

    </section>
  );
}
