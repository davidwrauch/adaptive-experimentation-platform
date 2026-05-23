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
              <h2 id="guided-title">Dashboard Guide</h2>
              <button onClick={() => setOpen(false)}>Open Dashboard</button>
            </div>
            <p>
              Northstar is a fictional subscription platform using adaptive experimentation to
              choose lifecycle messages while balancing engagement, retention, fatigue, unsubscribe
              risk, incremental lift, and rollout safety.
            </p>
            <div className="guide-summary">
              <div>
                <span>Primary metric</span>
                <strong>Incremental retention-adjusted engagement</strong>
              </div>
              <div>
                <span>Secondary and guardrail metrics</span>
                <strong>
                  immediate response, long-term retention, unsubscribe risk, fatigue exposure,
                  incremental lift, rollout safety
                </strong>
              </div>
            </div>
            <div className="guide-strategy-list">
              <p><strong>Static A/B Control:</strong> fixed baseline/control.</p>
              <p><strong>Epsilon Greedy:</strong> explores aggressively for short-term response.</p>
              <p><strong>Thompson Sampling:</strong> balances uncertainty and reward.</p>
              <p><strong>LinUCB:</strong> personalizes using user context and longer-term outcomes.</p>
            </div>
            <div className="guide-hold-note">
              <strong>Hold Expansion</strong>
              <p>
                Hold Expansion means the experiment is not a failure. It means the system sees
                promising evidence but recommends more data or risk reduction before broader rollout.
              </p>
            </div>
            <div className="guided-actions">
              <button onClick={() => setOpen(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
