const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export function fetchMetrics() {
  return fetchMetricsSummary();
}

export function fetchMetricsSummary() {
  return request("/metrics/summary");
}

export function fetchMetricsDetails() {
  return request("/metrics/details");
}

export function fetchEvents(limit = 25) {
  return fetchRecentEvents(limit);
}

export function fetchRecentEvents(limit = 25) {
  return request(`/events/recent?limit=${limit}`);
}

export function streamDemoStep(batchSize = 25) {
  return request("/demo/stream-step", {
    method: "POST",
    body: JSON.stringify({ batch_size: batchSize }),
  });
}

export function startReplay(config) {
  return request("/replay/start", {
    method: "POST",
    body: JSON.stringify({
      source: config.source,
      batch_size: config.batchSize,
      replay_speed_seconds: config.replaySpeedSeconds,
    }),
  });
}

export function pauseReplay() {
  return request("/replay/pause", { method: "POST" });
}

export function fetchReplayStatus() {
  return request("/replay/status");
}

export function fetchUpliftMetrics() {
  return request("/metrics/uplift");
}

export function fetchPolicyVersions() {
  return request("/policies/versions");
}

export function createPolicyVersion(payload) {
  return request("/policies/versions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function promotePolicyVersion(payload) {
  return request("/policies/promote", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function rollbackPolicyVersion(payload) {
  return request("/policies/rollback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchDecisionRecords(limit = 10) {
  return request(`/decision-records?limit=${limit}`);
}

export function createDecisionRecord(payload) {
  return request("/decision-records", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function recommendAssignment(context = sampleUserContext()) {
  return request("/assignments/recommend", {
    method: "POST",
    body: JSON.stringify({
      user_id: "sample-dashboard-user",
      requested_policy: "linucb",
      context,
    }),
  });
}

export function sampleUserContext() {
  return {
    engagement: 0.64,
    engagement_score: 0.64,
    fatigue_score: 0.22,
    profile_maturity: 0.85,
    unsubscribe_risk: 0.08,
    prior_touch_count: 5,
    days_since_last_touch: 9,
    prior_sessions: 8,
  };
}

export function fetchPolicyControls() {
  return request("/controls/policies");
}

export function updatePolicyControl(policy, payload) {
  return request(`/controls/policies/${policy}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function pausePolicy(policy) {
  return request(`/controls/policies/${policy}/pause`, { method: "POST" });
}

export function resumePolicy(policy) {
  return request(`/controls/policies/${policy}/resume`, { method: "POST" });
}

export function generateMessaging(context = sampleUserContext()) {
  return request("/messaging/generate", {
    method: "POST",
    body: JSON.stringify({
      user_id: "sample-dashboard-user",
      policy: "linucb",
      context,
    }),
  });
}
