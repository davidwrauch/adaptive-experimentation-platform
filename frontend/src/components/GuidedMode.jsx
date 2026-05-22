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
              This platform simulates a lifecycle messaging system choosing email, SMS, and push
              interventions while balancing clicks, retention, fatigue, unsubscribe risk, and safe rollout.
            </p>
            <div className="guided-grid">
              <GuideItem
                title="Policies"
                body="Static Control is the baseline. Epsilon Greedy explores more. Thompson Sampling uses uncertainty. LinUCB uses user context to personalize decisions."
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
