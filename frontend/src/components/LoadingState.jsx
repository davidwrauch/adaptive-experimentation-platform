import React from "react";

export default function LoadingState({ retryCount = 0 }) {
  return (
    <section className="loading-console">
      <div className="loading-pulse" />
      <div>
        <p className="eyebrow">Hosted demo warming up</p>
        <h2>Backend is waking up, retrying...</h2>
        <p>
          Hosted demo usually loads in 5-15 seconds. Once awake, interactions should be faster.
        </p>
        <p>
          This platform replays lifecycle messaging traffic, compares adaptive policies, estimates
          long-term and incremental value, and applies governance before rollout.
        </p>
        <small>Retry attempt {retryCount + 1} of 4</small>
      </div>
    </section>
  );
}
