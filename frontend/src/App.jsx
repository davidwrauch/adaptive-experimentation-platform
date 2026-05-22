import React, { useCallback, useEffect, useState } from "react";
import {
  fetchMetricsDetails,
  fetchMetricsSummary,
  fetchRecentEvents,
  fetchUpliftMetrics,
  simulateDecision,
  streamDemoStep,
} from "./api";
import AssignmentPanel from "./components/AssignmentPanel";
import BayesianPanel from "./components/BayesianPanel";
import DashboardSection from "./components/DashboardSection";
import DecisionLogPanel from "./components/DecisionLogPanel";
import DemoScenario from "./components/DemoScenario";
import EventStream from "./components/EventStream";
import ExperimentConfidencePanel from "./components/ExperimentConfidencePanel";
import ExplorationBudgetPanel from "./components/ExplorationBudgetPanel";
import GovernancePanel from "./components/GovernancePanel";
import GuidedMode from "./components/GuidedMode";
import LaunchIntelligencePanel from "./components/LaunchIntelligencePanel";
import LoadingState from "./components/LoadingState";
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
  const [uplift, setUplift] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retryCount, setRetryCount] = useState(0);
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
      const [metricsBody, eventsBody, upliftBody] = await Promise.all([
        includeDetails ? fetchMetricsDetails() : fetchMetricsSummary(),
        fetchRecentEvents(50),
        fetchUpliftMetrics().catch(() => null),
      ]);
      setMetrics(metricsBody);
      setEvents(eventsBody);
      if (upliftBody) {
        setUplift(upliftBody);
      }
      setLastUpdated(new Date());
      setLoading(false);
    } catch (err) {
      setError("Backend is waking up, retrying...");
      throw err;
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadWithRetry() {
      for (let attempt = 0; attempt < 4; attempt += 1) {
        try {
          setRetryCount(attempt);
          await refresh();
          return;
        } catch (err) {
          if (cancelled) return;
          await sleep(2500);
        }
      }
      setLoading(false);
      setError("Hosted backend is still waking up. Use Refresh Details in a moment.");
    }
    loadWithRetry();
    return () => {
      cancelled = true;
    };
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

  async function handleRefreshDetails() {
    try {
      await refresh(true);
    } catch (err) {
      // The visible warming message already explains the transient hosted-demo state.
    }
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
          <button className="refresh-button" onClick={handleRefreshDetails}>Refresh Details</button>
        </div>
      </header>

      {error && <div className="alert">{error}</div>}
      {loading ? (
        <LoadingState retryCount={retryCount} />
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
                uplift={uplift}
                liveMode={liveMode}
                liveTick={liveTick}
                lastUpdated={lastUpdated}
              />
              <LaunchIntelligencePanel metrics={metrics} uplift={uplift} liveTick={liveTick} />
              <ExperimentConfidencePanel metrics={metrics} />
              <section className="panel overview-explainer">
                <h2>How to read this dashboard</h2>
                <div className="overview-guide-grid">
                  <div><strong>Optimizing</strong><span>Clicks, retention, incremental lift, and safe rollout.</span></div>
                  <div>
                    <strong>Operational Risks</strong>
                    <span>
                      Policies may over-contact users, drift over time, or optimize short-term
                      engagement at the expense of long-term customer value.
                    </span>
                  </div>
                  <div><strong>Decision supported</strong><span>Promote, continue, monitor, roll back, or send to human review.</span></div>
                </div>
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
                <ExperimentConfidencePanel metrics={metrics} />
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

function sleep(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
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
