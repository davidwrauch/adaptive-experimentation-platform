import React, { useEffect, useState } from "react";

export default function GuidedMode() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const seen = window.localStorage.getItem("guided-mode-seen");
    if (!seen) {
      setOpen(true);
      window.localStorage.setItem("guided-mode-seen", "true");
    }
  }, []);

  return (
    <>
      <button className="guided-button" onClick={() => setOpen(true)}>
        Dashboard Guide
      </button>
      {open && (
        <div className="guided-overlay" role="dialog" aria-modal="true" aria-labelledby="guided-title">
          <div className="guided-card">
            <div className="section-heading">
              <h2 id="guided-title">How to read this dashboard</h2>
              <button onClick={() => setOpen(false)}>Close</button>
            </div>
            <p>
              Northstar is a fictional subscription platform using adaptive experimentation to
              choose lifecycle messages. This lifecycle messaging system treats users as
              subscribers or marketplace participants,
              interventions are approved email, SMS, and push message strategies, and policies
              decide which message style to send based on user state and governance constraints.
            </p>
            <div className="guided-grid">
              <GuideItem
                title="What is being optimized"
                body="The system supports onboarding completion, re-engagement, retention, churn prevention, subscription renewal, and marketplace activity."
              />
              <GuideItem
                title="Message experiments"
                body="Northstar tests message timing, frequency, length, personalization depth, cadence, urgency, and intervention category without allowing unrestricted copy generation."
              />
              <GuideItem
                title="Policies"
                body="Static Control is the baseline. Epsilon Greedy explores more and can over-sample urgency reminders. Thompson Sampling balances uncertainty and reward. LinUCB adapts to user context and retention tradeoffs."
              />
              <GuideItem
                title="Business outcomes"
                body="Immediate reward approximates clicks. Long-term reward incorporates retention, fatigue, and churn risk so short-term wins do not hide customer harm."
              />
              <GuideItem
                title="Governance"
                body="Launch labels convert model evidence into operational decisions: deploy, canary, human review, or pause."
              />
              <GuideItem
                title="Live mode"
                body="Live simulation appends small event batches over time so the dashboard behaves like an operations view without overloading the hosted backend."
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function GuideItem({ title, body }) {
  return (
    <article>
      <strong>{title}</strong>
      <p>{body}</p>
    </article>
  );
}
