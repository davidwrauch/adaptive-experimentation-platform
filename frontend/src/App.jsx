import React, { useCallback, useEffect, useState } from "react";
import { fetchEvents, fetchMetrics, simulateDecision } from "./api";
import AssignmentPanel from "./components/AssignmentPanel";
import BayesianPanel from "./components/BayesianPanel";
import DemoScenario from "./components/DemoScenario";
import EventStream from "./components/EventStream";
import ExplorationBudgetPanel from "./components/ExplorationBudgetPanel";
import GovernancePanel from "./components/GovernancePanel";
import MetricsCards from "./components/MetricsCards";
import MessagingGenerationPanel from "./components/MessagingGenerationPanel";
import ObservabilityPanel from "./components/ObservabilityPanel";
import PolicyDashboard from "./components/PolicyDashboard";
import RiskMonitoringPanel from "./components/RiskMonitoringPanel";
import RolloutControlsPanel from "./components/RolloutControlsPanel";
import StreamingStatusPanel from "./components/StreamingStatusPanel";
import TradeoffPanel from "./components/TradeoffPanel";

export default function App() {
  const [metrics, setMetrics] = useState({ total_events: 0, policies: [] });
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      setError("");
      const [metricsBody, eventsBody] = await Promise.all([fetchMetrics(), fetchEvents()]);
      setMetrics(metricsBody);
      setEvents(eventsBody);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  async function handleSimulate(policy) {
    await simulateDecision(policy);
    await refresh();
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Adaptive Experimentation</p>
          <h1>AI Decisioning Dashboard</h1>
        </div>
        <button className="refresh-button" onClick={refresh}>Refresh</button>
      </header>

      {error && <div className="alert">{error}</div>}
      {loading ? (
        <div className="empty-state">Loading platform metrics...</div>
      ) : (
        <>
          <DemoScenario />
          <MetricsCards metrics={metrics} />
          <StreamingStatusPanel streaming={metrics.streaming} />
          <ObservabilityPanel observability={metrics.observability} />
          <RolloutControlsPanel rollout={metrics.rollout} onChanged={refresh} />
          <AssignmentPanel />
          <MessagingGenerationPanel />
          <PolicyDashboard metrics={metrics} onSimulate={handleSimulate} />
          <GovernancePanel metrics={metrics} />
          <ExplorationBudgetPanel exploration={metrics.exploration} />
          <BayesianPanel bayesian={metrics.bayesian} />
          <TradeoffPanel metrics={metrics} />
          <RiskMonitoringPanel metrics={metrics} />
          <EventStream events={events} />
        </>
      )}
    </main>
  );
}
