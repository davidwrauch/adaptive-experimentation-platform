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


def test_overview_and_experimentation_have_distinct_purpose():
    app = read("frontend/src/App.jsx")
    overview_block = app.split('{activeTab === "Overview" && (', 1)[1].split(
        '{activeTab === "Experimentation" && (',
        1,
    )[0]
    experimentation_block = app.split('{activeTab === "Experimentation" && (', 1)[1].split(
        '{activeTab === "Risk & Governance" && (',
        1,
    )[0]

    assert "MetricsCards" in overview_block
    assert "How to read this dashboard" in overview_block
    assert "ExperimentConfidencePanel" not in overview_block
    assert "LaunchIntelligencePanel" not in overview_block
    assert "ExperimentConfidencePanel" in experimentation_block
    assert "BayesianPanel" in experimentation_block
    assert "UpliftPanel" in experimentation_block
    assert "ExplorationBudgetPanel" in experimentation_block


def test_loading_and_retry_copy_is_polished():
    loading = read("frontend/src/components/LoadingState.jsx")
    app = read("frontend/src/App.jsx")
    styles = read("frontend/src/styles.css")

    assert "Hosted demo usually loads in 5-15 seconds." in loading
    assert "Once awake, interactions should be faster." in loading
    assert "Backend is waking up, retrying..." in loading
    assert "Adaptive Experimentation Platform" in loading
    for capability in [
        "Contextual bandits",
        "Bayesian experimentation",
        "OPE",
        "Causal uplift",
        "Governance",
        "Live replay",
    ]:
        assert capability in loading
    assert "skeleton-dashboard" in loading
    assert "skeleton-card" in loading
    assert "skeleton-panel" in loading
    assert ".skeleton-card" in styles
    assert ".skeleton-panel" in styles
    assert "retryCount" in app
    assert "loadWithRetry" in app


def test_policy_simulation_control_has_visible_feedback():
    dashboard = read("frontend/src/components/PolicyDashboard.jsx")

    assert "Run policy simulation" in dashboard
    assert "Events added" in dashboard
    assert "Policy simulated" in dashboard
    assert "Reward effect" in dashboard
    assert "Updated" in dashboard
    assert "simulating" in dashboard
    assert "Simulate {formatPolicyLabel(policy)}" not in dashboard


def test_rollout_controls_use_clear_percentage_language():
    rollout = read("frontend/src/components/RolloutControlsPanel.jsx")

    assert "Traffic cap" in rollout
    assert "Canary rollout" in rollout
    assert "Maximum share of eligible traffic this policy is allowed to receive." in rollout
    assert (
        "Small initial rollout percentage used to test a policy safely before broader expansion."
        in rollout
    )
    assert "Use these controls to slow, pause, or safely expand a policy before full deployment." in rollout
    assert "Save rollout" in rollout
    assert "Pause policy" in rollout
    assert "Resume policy" in rollout
    assert "formatPercent" in rollout
    assert ">cap<" not in rollout
    assert ">canary<" not in rollout


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
    assert "Continue Rollout" in helpers
    assert "Hold Expansion" in helpers
    assert "Human Review Recommended" in helpers
    assert "Insufficient Evidence" in helpers
    assert "formatPolicyLabel(bestPolicy?.policy)" in metrics


def test_executive_overview_visual_scorecards_and_launch_badge():
    metrics = read("frontend/src/components/MetricsCards.jsx")
    styles = read("frontend/src/styles.css")

    assert "Traffic" in metrics
    assert "Short-term winner" in metrics
    assert "Long-term winner" in metrics
    assert "Launch posture" in metrics
    assert "overview-scorecard-row" in metrics
    assert "Raw reward winner" in metrics
    assert "Operational recommendation" in metrics
    assert "launch-badge" in metrics
    assert ".overview-scorecard-row" in styles
    assert ".mini-score-card" in styles


def test_primary_ui_avoids_raw_lowercase_rollback_copy():
    metrics = read("frontend/src/components/MetricsCards.jsx")
    launch = read("frontend/src/components/LaunchIntelligencePanel.jsx")

    assert "Rollback Recommended" in metrics + launch
    assert ">{rollback}<" not in metrics
    assert "rollback posture" not in metrics


def test_experiment_confidence_and_statistical_posture_rendering():
    app = read("frontend/src/App.jsx")
    panel = read("frontend/src/components/ExperimentConfidencePanel.jsx")
    helpers = read("frontend/src/interpretations.js")

    assert "ExperimentConfidencePanel" in app
    assert "Experiment Confidence" in panel
    assert "Experiment Result" in panel
    assert "Operational Recommendation" in panel
    assert "Likely Positive" in helpers
    assert "Directionally Positive" in helpers
    assert "Inconclusive" in helpers
    assert "Underpowered" in helpers
    assert "High Variance" in helpers
    assert "Likely Negative" in helpers


def test_overview_uses_operational_risks_copy():
    app = read("frontend/src/App.jsx")

    assert "Operational Risks" in app
    assert "Can go wrong" not in app
    assert "Policies may over-contact users, drift over time" in app


def test_primary_ui_uses_professional_policy_labels():
    components = [
        "frontend/src/components/MetricsCards.jsx",
        "frontend/src/components/PolicyDashboard.jsx",
        "frontend/src/components/TradeoffPanel.jsx",
        "frontend/src/components/GovernancePanel.jsx",
        "frontend/src/components/BayesianPanel.jsx",
        "frontend/src/components/RiskMonitoringPanel.jsx",
        "frontend/src/components/UpliftPanel.jsx",
        "frontend/src/components/EventStream.jsx",
        "frontend/src/components/AssignmentPanel.jsx",
    ]

    for path in components:
        content = read(path)
        assert "formatPolicyLabel" in content, path


def test_epsilon_greedy_tradeoff_copy_is_explicit():
    helpers = read("frontend/src/interpretations.js")
    guided = read("frontend/src/components/GuidedMode.jsx")

    assert "Epsilon Greedy" in helpers
    assert "short-term clicks" in helpers
    assert "stronger long-term retention" in helpers
    assert "Epsilon Greedy explores more" in guided


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
