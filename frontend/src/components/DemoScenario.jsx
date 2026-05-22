import React from "react";

export default function DemoScenario() {
  return (
    <section className="scenario-band">
      <div>
        <p className="eyebrow">Demo scenario</p>
        <h2>Northstar lifecycle messaging console</h2>
        <p>
          Northstar is a fictional subscription platform optimizing lifecycle engagement and
          retention. The system tests message timing, frequency, length, personalization depth,
          and intervention strategy while balancing clicks, retention, fatigue, unsubscribe risk,
          incremental value, and rollout safety.
        </p>
      </div>
      <div className="why-box">
        <strong>Why this matters</strong>
        <span>
          The highest-click policy can be the wrong policy if it burns out users or raises
          unsubscribe risk. This demo shows why short-term response and long-term customer value
          need separate decision paths.
        </span>
      </div>
    </section>
  );
}
