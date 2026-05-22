import React, { useEffect, useState } from "react";
import { fetchReplayStatus, pauseReplay, startReplay } from "../api";
import { HelpLabel, WhyThisMatters } from "./InfoTooltip";

export default function ReplayControlsPanel({ onTick }) {
  const [source, setSource] = useState("synthetic");
  const [batchSize, setBatchSize] = useState(25);
  const [speed, setSpeed] = useState(7);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchReplayStatus().then(setStatus).catch(() => setError("Replay status is warming up."));
  }, []);

  useEffect(() => {
    if (!status?.running) {
      return undefined;
    }
    const timer = window.setInterval(runReplayStep, Math.max(1, speed) * 1000);
    return () => window.clearInterval(timer);
  }, [status?.running, source, batchSize, speed]);

  async function runReplayStep() {
    try {
      setError("");
      const body = await startReplay({
        source,
        batchSize: Number(batchSize),
        replaySpeedSeconds: Number(speed),
      });
      setStatus(body);
      onTick?.();
    } catch (err) {
      setError("Replay paused while the backend warms up. Try again shortly.");
      await handlePause();
    }
  }

  async function handleStart() {
    await runReplayStep();
  }

  async function handlePause() {
    const body = await pauseReplay();
    setStatus(body);
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <h2>
          <HelpLabel help="What: browser-driven replay controls for synthetic or Open Bandit logged events. Why: lets reviewers watch evidence accumulate over time. Good: steady replay with fresh metrics. Bad: paused status or backend warming errors. Action: lower batch size or pause before changing source.">
            Replay controls
          </HelpLabel>
        </h2>
        <span className={status?.running ? "status-pill status-deploy" : "status-pill status-canary"}>
          {status?.running ? "running" : "paused"}
        </span>
      </div>
      <p className="panel-copy">
        Synthetic replay uses the deterministic lifecycle messaging simulator. Open Bandit replay
        uses logged recommendation-style actions, rewards, and propensities; set `OPEN_BANDIT_CSV_PATH`
        on the backend to replay a downloaded CSV, otherwise the demo uses a tiny built-in sample.
      </p>
      <WhyThisMatters>
        Replay controls make the dashboard feel like an operations system: event evidence arrives,
        summaries update, and governance/observability respond without rescanning the full warehouse.
      </WhyThisMatters>
      {error && <div className="alert">{error}</div>}
      <div className="replay-grid">
        <label>
          Source
          <select value={source} onChange={(event) => setSource(event.target.value)}>
            <option value="synthetic">Synthetic replay</option>
            <option value="open_bandit">Open Bandit replay</option>
          </select>
        </label>
        <label>
          Batch size
          <input
            type="number"
            min="1"
            max="250"
            value={batchSize}
            onChange={(event) => setBatchSize(event.target.value)}
          />
        </label>
        <label>
          Replay speed
          <input
            type="number"
            min="1"
            max="60"
            value={speed}
            onChange={(event) => setSpeed(event.target.value)}
          />
        </label>
        <button onClick={handleStart}>Start replay</button>
        <button onClick={handlePause}>Pause</button>
      </div>
      <div className="compact-grid replay-status">
        <span>Total replayed</span>
        <strong>{status?.total_replayed_events ?? 0}</strong>
        <span>Last batch</span>
        <strong>{status?.last_batch_added ?? 0}</strong>
        <span>Status</span>
        <strong>{status?.message ?? "Replay has not started."}</strong>
      </div>
    </section>
  );
}
