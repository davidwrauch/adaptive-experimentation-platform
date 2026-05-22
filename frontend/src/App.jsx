import React, { useCallback, useEffect, useState } from "react";
import {
  fetchMetricsDetails,
  fetchMetricsSummary,
  fetchRecentEvents,
  simulateDecision,
  streamDemoStep,
} from "./api";
import AssignmentPanel from "./components/AssignmentPanel";
import BayesianPanel from "./components/BayesianPanel";
import DashboardSection from "./components/DashboardSection";
import DecisionLogPanel from "./components/DecisionLogPanel";
import DemoScenario from "./components/DemoScenario";
import EventStream from "./components/EventStream";
import ExplorationBudgetPanel from "./components/ExplorationBudgetPanel";
import GovernancePanel from "./components/GovernancePanel";
import GuidedMode from "./components/GuidedMode";
import MetricsCards from "./components/MetricsCards";
import MessagingGenerationPanel from "./components/MessagingGenerationPanel";
import ObservabilityPanel from "./components/ObservabilityPanel";
import PolicyDashboard from "./components/PolicyDashboard";
import PolicyLifecyclePanel from "./components/PolicyLifecyclePanel";
import RiskMonitoringPanel from "./components/RiskMonitoringPanel";
import RolloutControlsPanel from "./components/RolloutControlsPanel";
import ReplayControlsPanel from "./components/ReplayControlsPanel";
import StreamingStatusPanel from "./components/StreamingStatusPanel";
import TradeoffPanel from "./components/TradeoffPanel";
import UpliftPanel from "./components/UpliftPanel";
import { HelpLabel } from "./components/InfoTooltip";

const LIVE_INTERVAL_SECONDS = 10;
const TABS = [
  "Overview",
  "Experimentation",
  "Risk & Governance",
  "Live Operations",
  "AI & Decision Support",
];

export default function App() {
  const [metrics, setMetrics] = useState({ total_events: 0, policies: [] });
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [liveMode, setLiveMode] = useState(false);
  const [liveTick, setLiveTick] = useState({
    event_count_added: 0,
    total_events: 0,
    latest_timestamp: null,
  });
  const [lastUpdated, setLastUpdated] = useState(null);
  const [nextUpdateIn, setNextUpdateIn] = useState(LIVE_INTERVAL_SECONDS);
  const [activeTab, setActiveTab] = useState("Overview");

  const refresh = useCallback(async (includeDetails = false) => {
    try {
      setError("");
      const [metricsBody, eventsBody] = await Promise.all([
        includeDetails ? fetchMetricsDetails() : fetchMetricsSummary(),
        fetchRecentEvents(50),
      ]);
      setMetrics(metricsBody);
      setEvents(eventsBody);
      setLastUpdated(new Date());
    } catch (err) {
      setError("The backend may be waking up. Please wait a moment and refresh.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!liveMode) {
      setNextUpdateIn(LIVE_INTERVAL_SECONDS);
      return undefined;
    }
    setNextUpdateIn(LIVE_INTERVAL_SECONDS);
    const countdown = window.setInterval(() => {
      setNextUpdateIn((value) => (value <= 1 ? LIVE_INTERVAL_SECONDS : value - 1));
    }, 1000);
    const timer = window.setInterval(async () => {
      try {
        setError("");
        const tick = await streamDemoStep(25);
        setLiveTick(tick);
        await refresh();
        setNextUpdateIn(LIVE_INTERVAL_SECONDS);
      } catch (err) {
        setError("Live simulation paused while the backend wakes up. Try again shortly.");
        setLiveMode(false);
      }
    }, LIVE_INTERVAL_SECONDS * 1000);
    return () => {
      window.clearInterval(timer);
      window.clearInterval(countdown);
    };
  }, [liveMode, refresh]);

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
        <div className="topbar-actions">
          <GuidedMode />
          <button
            className={liveMode ? "live-toggle live-toggle-paused" : "live-toggle live-toggle-start"}
            onClick={() => setLiveMode((value) => !value)}
          >
            {liveMode ? "Pause Live Simulation" : "Start Live Simulation"}
          </button>
          <button className="refresh-button" onClick={() => refresh(true)}>Refresh Details</button>
        </div>
      </header>

      {error && <div className="alert">{error}</div>}
      {loading ? (
        <div className="empty-state">Loading platform metrics...</div>
      ) : (
        <>
          <nav className="tab-nav" aria-label="Dashboard sections">
            {TABS.map((tab) => (
              <button
                className={activeTab === tab ? "tab-button active" : "tab-button"}
                key={tab}
                onClick={() => setActiveTab(tab)}
                type="button"
              >
                {tab}
              </button>
            ))}
          </nav>

          {activeTab === "Overview" && (
            <div className="tab-panel">
              <DemoScenario />
              <MetricsCards
                metrics={metrics}
                liveMode={liveMode}
                liveTick={liveTick}
                lastUpdated={lastUpdated}
              />
              <section className="panel overview-explainer">
                <h2>What this system is doing</h2>
                <p>
                  The platform is replaying lifecycle messaging decisions, comparing adaptive
                  policies, tracking long-term customer impact, and applying governance before any
                  policy would be expanded. Use the tabs for deeper experiment, risk, operations,
                  and AI decision-support detail.
                </p>
              </section>
            </div>
          )}

          {activeTab === "Experimentation" && (
            <div className="tab-panel">
              <DashboardSection
                title="Experimentation"
                description="Compare immediate lift, long-term value, offline estimates, Bayesian confidence, and exploration budgets."
              >
                <PolicyDashboard metrics={metrics} onSimulate={handleSimulate} />
                <TradeoffPanel metrics={metrics} />
                <GovernancePanel metrics={metrics} />
                <UpliftPanel />
                <BayesianPanel bayesian={metrics.bayesian} />
                <ExplorationBudgetPanel exploration={metrics.exploration} />
              </DashboardSection>
            </div>
          )}

          {activeTab === "Risk & Governance" && (
            <div className="tab-panel">
              <DashboardSection
                title="Risk & Governance"
                description="Translate evidence, uncertainty, fatigue, and risk signals into rollout actions."
              >
                <ObservabilityPanel observability={metrics.observability} />
                <GovernancePanel metrics={metrics} />
                <PolicyLifecyclePanel />
                <RolloutControlsPanel rollout={metrics.rollout} onChanged={refresh} />
                <RiskMonitoringPanel metrics={metrics} />
                <DecisionLogPanel metrics={metrics} />
              </DashboardSection>
            </div>
          )}

          {activeTab === "Live Operations" && (
            <div className="tab-panel">
              <DashboardSection
                title="Live Operations"
                description="Control live simulation and replay, monitor transport status, and inspect compact audit logs."
              >
                <LiveSimulationPanel
                  liveMode={liveMode}
                  liveTick={liveTick}
                  metrics={metrics}
                  nextUpdateIn={nextUpdateIn}
                  lastUpdated={lastUpdated}
                />
                <ReplayControlsPanel onTick={refresh} />
                <StreamingStatusPanel streaming={metrics.streaming} />
                <EventStream events={events} />
              </DashboardSection>
            </div>
          )}

          {activeTab === "AI & Decision Support" && (
            <div className="tab-panel">
              <DashboardSection
                title="AI & Decision Support"
                description="Review evidence retrieval, similarity-informed explanations, constrained messaging, and human review routing."
              >
                <AssignmentPanel />
                <MessagingGenerationPanel />
              </DashboardSection>
            </div>
          )}
        </>
      )}
    </main>
  );
}

function LiveSimulationPanel({ liveMode, liveTick, metrics, nextUpdateIn, lastUpdated }) {
  return (
    <section className="panel live-panel">
      <div>
        <div className={liveMode ? "live-dot active" : "live-dot"} />
        <div>
          <h2>
            <HelpLabel
              help="Live simulation appends small batches of deterministic lifecycle events. Good: steady growth with low errors. Bad: repeated failures or no new events. Operator action: pause if the backend is warming up, then resume when healthy."
            >
              <span className="live-title">
                <span className={liveMode ? "live-pulse active" : "live-pulse"} />
                {liveMode ? "Live simulation running" : "Live simulation paused"}
              </span>
            </HelpLabel>
          </h2>
          <p className="panel-copy">
            Adds small batches of replayed lifecycle-message events over time, then refreshes fast
            summary metrics so the hosted demo feels active without recomputing the full event table.
          </p>
        </div>
      </div>
      <div className="live-stats">
        <span>Total events <strong>{metrics.total_events.toLocaleString()}</strong></span>
        <span>Events added in last tick <strong>{liveTick.event_count_added}</strong></span>
        <span>Next update <strong>{liveMode ? `${nextUpdateIn}s` : "paused"}</strong></span>
        <span>Updated <strong>{formatUpdated(lastUpdated)}</strong></span>
      </div>
    </section>
  );
}

function formatUpdated(value) {
  if (!value) {
    return "pending";
  }
  return value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
