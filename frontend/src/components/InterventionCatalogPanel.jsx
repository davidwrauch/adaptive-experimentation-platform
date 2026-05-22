import React from "react";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

const interventions = [
  {
    name: "Short reminder",
    message: "Complete your setup to unlock personalized recommendations.",
    length: "Short",
    personalization: "Low",
    frequency: "High-frequency",
    fatigue: "Medium",
    unsubscribeRisk: "Medium",
    tone: "Direct",
  },
  {
    name: "Personalized recommendation summary",
    message: "New recommendations matching your interests are waiting.",
    length: "Medium",
    personalization: "High",
    frequency: "Moderate",
    fatigue: "Low",
    unsubscribeRisk: "Low",
    tone: "Helpful",
  },
  {
    name: "Weekly digest",
    message: "You have unread updates from creators you follow.",
    length: "Medium",
    personalization: "Medium",
    frequency: "Weekly",
    fatigue: "Low",
    unsubscribeRisk: "Low",
    tone: "Informational",
  },
  {
    name: "Win-back message",
    message: "We saved a few recommendations to help you get back on track.",
    length: "Medium",
    personalization: "Medium",
    frequency: "Low-frequency",
    fatigue: "Medium",
    unsubscribeRisk: "Medium",
    tone: "Supportive",
  },
  {
    name: "Urgency reminder",
    message: "Your saved recommendations may expire soon.",
    length: "Short",
    personalization: "Low",
    frequency: "High-frequency",
    fatigue: "High",
    unsubscribeRisk: "High",
    tone: "Urgent",
  },
  {
    name: "Educational onboarding tip",
    message: "Follow three topics so Northstar can tailor your weekly recommendations.",
    length: "Longer",
    personalization: "Medium",
    frequency: "Low-frequency",
    fatigue: "Low",
    unsubscribeRisk: "Low",
    tone: "Educational",
  },
];

export default function InterventionCatalogPanel() {
  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="Northstar tests lifecycle messages, not abstract variants. Policies choose when to send, how often to send, how personalized the message should be, and which intervention strategy fits the user state.">
            Intervention catalog
          </HelpLabel>
        </h2>
        <span className="status-pill status-canary">Human review required</span>
      </div>
      <p className="panel-copy">
        Northstar is a fictional subscription platform optimizing onboarding, re-engagement,
        retention, churn prevention, subscription renewal, and marketplace activity.
      </p>
      <WhyThisMatters>
        The adaptive system experiments with message timing, frequency, length, personalization
        depth, and intervention strategy while balancing clicks, retention, fatigue, unsubscribe
        risk, incremental value, and rollout safety.
      </WhyThisMatters>

      <div className="optimization-grid">
        {["Onboarding completion", "Re-engagement", "Retention", "Churn prevention", "Subscription renewal", "Marketplace activity"].map((goal) => (
          <span key={goal}>{goal}</span>
        ))}
      </div>

      <div className="intervention-grid">
        {interventions.map((intervention) => (
          <article className="intervention-card" key={intervention.name}>
            <strong>{intervention.name}</strong>
            <p>"{intervention.message}"</p>
            <dl>
              <dt>Length</dt>
              <dd>{intervention.length}</dd>
              <dt>Personalization</dt>
              <dd>{intervention.personalization}</dd>
              <dt>Frequency</dt>
              <dd>{intervention.frequency}</dd>
              <dt>Fatigue</dt>
              <dd>{intervention.fatigue}</dd>
              <dt>Unsubscribe risk</dt>
              <dd>{intervention.unsubscribeRisk}</dd>
              <dt>Tone</dt>
              <dd>{intervention.tone}</dd>
            </dl>
          </article>
        ))}
      </div>

      <div className="selected-intervention-grid">
        <article>
          <span>Selected intervention</span>
          <strong>Personalized medium-length recommendation summary</strong>
          <p>
            User historically responds better to contextual recommendations with lower fatigue risk.
            Expected tradeoff: fewer immediate clicks than urgency copy, stronger retention.
          </p>
        </article>
        <article>
          <span>Alternative suppressed</span>
          <strong>High-frequency short reminder</strong>
          <p>
            Suppressed because elevated unsubscribe probability and recent touch count suggest the
            user may be over-contacted.
          </p>
        </article>
      </div>
    </section>
  );
}
