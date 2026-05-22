from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_tooltip_and_help_components_are_renderable():
    tooltip = read("frontend/src/components/InfoTooltip.jsx")

    assert "export default function InfoTooltip" in tooltip
    assert "export function HelpLabel" in tooltip
    assert "export function WhyThisMatters" in tooltip
    assert 'role="tooltip"' in tooltip
    assert 'aria-label={label}' in tooltip


def test_guided_mode_explains_platform_and_policy_differences():
    guided = read("frontend/src/components/GuidedMode.jsx")

    assert "Dashboard Guide" in guided
    assert "Guided Mode" not in guided
    assert "lifecycle messaging system" in guided
    assert "Static Control" in guided
    assert "Epsilon Greedy" in guided
    assert "Thompson Sampling" in guided
    assert "LinUCB" in guided
    assert "localStorage" in guided


def test_interpretation_helpers_include_operator_actions():
    helpers = read("frontend/src/interpretations.js")

    assert "policyPerformanceInsight" in helpers
    assert "riskInsight" in helpers
    assert "uncertaintyInsight" in helpers
    assert "severityInterpretation" in helpers
    assert "governanceExplanation" in helpers
    assert "Suggested" not in helpers
    assert "Reduce traffic" in helpers
    assert "Pause, roll back" in helpers
    assert "Keep it in canary or human review" in helpers


def test_dashboard_information_architecture_groups_major_sections():
    app = read("frontend/src/App.jsx")
    styles = read("frontend/src/styles.css")

    for section in [
        "Overview",
        "Experimentation",
        "Risk & Governance",
        "Live Operations",
        "AI & Decision Support",
    ]:
        assert section in app

    assert "DashboardSection" in app
    assert ".dashboard-section" in styles
    assert ".tooltip-card" in styles
    assert ".guided-overlay" in styles


def test_dashboard_uses_operational_tabs_for_major_workflows():
    app = read("frontend/src/App.jsx")
    styles = read("frontend/src/styles.css")

    for tab in [
        "Overview",
        "Experimentation",
        "Risk & Governance",
        "Live Operations",
        "AI & Decision Support",
    ]:
        assert tab in app

    assert "tab-nav" in app
    assert "tab-button active" in app
    assert "How to read this dashboard" in app
    assert "LiveSimulationPanel" in app
    assert "ReplayControlsPanel" in app
    assert "EventStream" in app
    assert "UpliftPanel" in app
    assert "PolicyLifecyclePanel" in app
    assert "DecisionLogPanel" in app
    assert ".tab-nav" in styles
    assert ".tab-panel" in styles


def test_loading_and_retry_copy_is_polished():
    loading = read("frontend/src/components/LoadingState.jsx")
    app = read("frontend/src/App.jsx")

    assert "Hosted demo usually loads in 5-15 seconds." in loading
    assert "Once awake, interactions should be faster." in loading
    assert "Backend is waking up, retrying..." in loading
    assert "retryCount" in app
    assert "loadWithRetry" in app


def test_policy_display_labels_and_launch_intelligence_rendering():
    helpers = read("frontend/src/interpretations.js")
    launch = read("frontend/src/components/LaunchIntelligencePanel.jsx")
    metrics = read("frontend/src/components/MetricsCards.jsx")

    assert "formatPolicyLabel" in helpers
    assert "Static Control" in helpers
    assert "Epsilon Greedy" in helpers
    assert "Thompson Sampling" in helpers
    assert "LinUCB" in helpers
    assert "Launch Intelligence" in launch
    assert "Launch safety" in launch
    assert "Promote" in helpers
    assert "Rollback Recommended" in helpers
    assert "Insufficient Evidence" in helpers
    assert "formatPolicyLabel(bestPolicy?.policy)" in metrics


def test_dashboard_includes_browser_replay_controls():
    app = read("frontend/src/App.jsx")
    replay = read("frontend/src/components/ReplayControlsPanel.jsx")

    assert "ReplayControlsPanel" in app
    assert "Synthetic replay" in replay
    assert "Open Bandit replay" in replay
    assert "startReplay" in replay
    assert "pauseReplay" in replay
    assert "OPEN_BANDIT_CSV_PATH" in replay


def test_major_panels_include_help_and_why_this_matters_copy():
    component_dir = ROOT / "frontend/src/components"
    panel_files = [
        "PolicyDashboard.jsx",
        "TradeoffPanel.jsx",
        "GovernancePanel.jsx",
        "ObservabilityPanel.jsx",
        "BayesianPanel.jsx",
        "ExplorationBudgetPanel.jsx",
        "RiskMonitoringPanel.jsx",
        "AssignmentPanel.jsx",
        "MessagingGenerationPanel.jsx",
        "RolloutControlsPanel.jsx",
        "ReplayControlsPanel.jsx",
    ]

    for filename in panel_files:
        content = (component_dir / filename).read_text(encoding="utf-8")
        assert "HelpLabel" in content, filename
        assert "WhyThisMatters" in content, filename
