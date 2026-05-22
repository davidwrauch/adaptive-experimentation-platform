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

    assert "Guided Mode" in guided
    assert "lifecycle messaging system" in guided
    assert "Static A/B" in guided
    assert "Epsilon-greedy" in guided
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
        "Experiment Performance",
        "Risk & Governance",
        "Live Operations",
        "Policy Intelligence",
        "Messaging & Assignment Support",
    ]:
        assert section in app

    assert "DashboardSection" in app
    assert ".dashboard-section" in styles
    assert ".tooltip-card" in styles
    assert ".guided-overlay" in styles


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
