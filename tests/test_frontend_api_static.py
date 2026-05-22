from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_api_helpers_include_persistent_control_update():
    api = (ROOT / "frontend/src/api.js").read_text(encoding="utf-8")

    assert "export function updatePolicyControl" in api
    assert 'method: "POST"' in api
    assert "/controls/policies/" in api


def test_dashboard_api_helpers_use_live_summary_endpoints():
    api = (ROOT / "frontend/src/api.js").read_text(encoding="utf-8")

    assert "export function fetchMetricsSummary" in api
    assert "export function fetchMetricsDetails" in api
    assert "export function fetchRecentEvents" in api
    assert "export function streamDemoStep" in api
    assert '"/metrics/summary"' in api
    assert '"/metrics/details"' in api
    assert '"/demo/stream-step"' in api
    assert "`/events/recent?limit=${limit}`" in api
    assert "export function startReplay" in api
    assert "export function pauseReplay" in api
    assert "export function fetchReplayStatus" in api
    assert '"/replay/start"' in api
    assert '"/replay/pause"' in api
    assert '"/replay/status"' in api
    assert "export function fetchUpliftMetrics" in api
    assert "export function fetchPolicyVersions" in api
    assert "export function createDecisionRecord" in api
    assert '"/metrics/uplift"' in api
    assert '"/policies/versions"' in api
    assert '"/decision-records"' in api
