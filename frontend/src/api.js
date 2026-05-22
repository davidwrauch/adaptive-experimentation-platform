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
  return request("/metrics");
}

export function fetchEvents(limit = 25) {
  return request(`/events?limit=${limit}`);
}

export function simulateDecision(policy) {
  return request("/policies/simulate", {
    method: "POST",
    body: JSON.stringify({
      policy,
      user_id: `dashboard-${Math.ceil(Math.random() * 1000)}`,
      context: {
        engagement: Number(Math.random().toFixed(3)),
        engagement_score: Number(Math.random().toFixed(3)),
        fatigue_score: Number((0.1 + Math.random() * 0.55).toFixed(3)),
        profile_maturity: [0.25, 0.5, 0.75, 1][Math.floor(Math.random() * 4)],
        unsubscribe_risk: Number((0.03 + Math.random() * 0.22).toFixed(3)),
        prior_touch_count: Math.floor(Math.random() * 12),
        days_since_last_touch: Math.floor(Math.random() * 21),
        prior_sessions: Math.floor(Math.random() * 12),
      },
    }),
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
