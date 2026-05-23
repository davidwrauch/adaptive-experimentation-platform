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
    assert "Northstar is a fictional subscription platform" in guided
    assert "Incremental retention-adjusted engagement" in guided
    assert "Static A/B Control" in guided
    assert "Epsilon Greedy" in guided
    assert "Thompson Sampling" in guided
    assert "LinUCB" in guided
    assert "Open Dashboard" in guided
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
    assert "LiveSimulationPanel" in app
    assert "ReplayControlsPanel" in app
    assert "EventStream" in app
    assert "UpliftPanel" in app
    assert "PolicyLifecyclePanel" in app
    assert "DecisionLogPanel" in app
    assert ".tab-nav" in styles
    assert ".tab-panel" in styles


def test_tabs_are_audience_oriented_and_lazy_loaded():
    app = read("frontend/src/App.jsx")

    assert "Audience: experimentation scientists, analysts, and advanced PMs" in app
    assert "Audience: governance, trust and safety, and launch oversight" in app
    assert "Audience: ML and platform engineers" in app
    assert "Audience: ML scientists and adaptive systems teams" in app
    assert "hydratedTabs" in app
    assert 'activeTab === "Experimentation"' in app
    assert 'includeDetails: true, includeUplift: true' in app
    assert 'activeTab === "Live Operations"' in app
    assert "includeRecent: true" in app


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
    assert overview_block.index("ExperimentComparisonPanel") < overview_block.index("MetricsCards")
    assert "ExperimentConfidencePanel" not in overview_block
    assert "LaunchIntelligencePanel" not in overview_block
    assert "How to read this dashboard" not in overview_block
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


def test_cached_dashboard_and_freshness_indicators_render():
    app = read("frontend/src/App.jsx")
    styles = read("frontend/src/styles.css")

    assert "DASHBOARD_CACHE_KEY" in app
    assert "readDashboardCache" in app
    assert "writeDashboardCache" in app
    assert "localStorage" in app
    assert "Showing cached dashboard from" in app
    assert "Refreshing latest metrics..." in app
    assert "Live updates connected" in app
    assert "generated_at" in app
    assert "last_event_timestamp" in app
    assert "cache_age_seconds" in app
    assert "freshness-strip" in app
    assert ".freshness-strip" in styles


def test_dashboard_guide_uses_current_pm_framing():
    guided = read("frontend/src/components/GuidedMode.jsx")
    styles = read("frontend/src/styles.css")

    assert "Incremental retention-adjusted engagement" in guided
    for metric in [
        "immediate response",
        "long-term retention",
        "unsubscribe risk",
        "fatigue exposure",
        "incremental lift",
        "rollout safety",
    ]:
        assert metric in guided
    assert "Static A/B Control" in guided
    assert "fixed baseline/control" in guided
    assert "explores aggressively for short-term response" in guided
    assert "balances uncertainty and reward" in guided
    assert "personalizes using user context and longer-term outcomes" in guided
    assert "Hold Expansion means the experiment is not a failure." in guided
    assert "more data or risk reduction before broader rollout" in guided
    assert "Business outcomes" not in guided
    assert "Live mode" not in guided
    assert "guided-grid" not in guided
    assert "max-width: min(680px, 94vw)" in styles
    assert "max-height: min(88vh, 680px)" in styles


def test_policy_performance_simulation_section_removed_from_primary_ui():
    app = read("frontend/src/App.jsx")

    assert "PolicyDashboard" not in app
    assert "Run policy simulation" not in app
    assert "simulateDecision" not in app


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
    assert "Confidence: directional, not launch-ready" in helpers
    assert "formatPolicyLabel(bestPolicy?.policy)" in metrics


def test_launch_posture_hierarchy_reserves_rollback_for_severe_cases():
    helpers = read("frontend/src/interpretations.js")

    assert 'state: "Rollback Recommended"' in helpers
    assert "criticalGuardrail && broadExposure" in helpers
    assert "severeLongTermHarm" in helpers
    assert "highRiskHighTraffic" in helpers
    assert 'state: "Hold Expansion"' in helpers
    assert "Insufficient confidence: collect more traffic before expanding a policy." in helpers
    assert (
        "Hold Expansion means the system is not calling the experiment a failure. It means the policy should not be expanded until traffic quality, saturation, or risk checks improve."
        in helpers
    )
    assert (
        "Rollback is reserved for already-expanded policies with severe safety or performance issues."
        in helpers
    )


def test_executive_overview_visual_scorecards_and_launch_badge():
    metrics = read("frontend/src/components/MetricsCards.jsx")
    helpers = read("frontend/src/interpretations.js")
    styles = read("frontend/src/styles.css")

    assert "Traffic" in metrics
    assert "Short-term winner" in metrics
    assert "Long-term winner" in metrics
    assert "Launch posture" in metrics
    assert "overview-scorecard-row" in metrics
    assert "Experiment result" in metrics
    assert "Long-term result" in metrics
    assert "Operational recommendation" in metrics
    assert "Evidence: mixed, guardrails active" in helpers
    assert "Confidence: directional, not launch-ready" in helpers
    assert "launch-badge" in metrics
    assert "confidence-line" in metrics
    assert ".confidence-line" in styles
    assert ".overview-scorecard-row" in styles
    assert ".mini-score-card" in styles


def test_pm_decision_card_and_confidence_badges_render():
    metrics = read("frontend/src/components/MetricsCards.jsx")
    styles = read("frontend/src/styles.css")

    assert "PM Decision Card" in metrics
    assert "Did it work, and should we expand?" in metrics
    assert "Experiment result" in metrics
    assert "Bayesian confidence" in metrics
    assert "Risk" in metrics
    assert "Recommendation" in metrics
    assert "Next action" in metrics
    assert "Why" in metrics
    assert "Hold expansion, reduce exposure to high-fatigue users, and collect more traffic before launch." in metrics
    assert "guardrails are active" in metrics
    assert "High confidence" in metrics
    assert "Directional evidence" in metrics
    assert "Mixed evidence" in metrics
    assert "Inconclusive" in metrics
    assert "Underpowered" in metrics
    assert "Probability best" in metrics
    assert "overview-confidence-strip" in metrics
    assert ".pm-decision-card" in styles
    assert ".overview-confidence-card" in styles


def test_overview_primary_secondary_metrics_and_probability_tooltip():
    metrics = read("frontend/src/components/MetricsCards.jsx")
    styles = read("frontend/src/styles.css")

    assert "Primary metric" in metrics
    assert "Incremental retention-adjusted engagement" in metrics
    assert "Secondary and guardrail metrics" in metrics
    for label in [
        "Immediate clicks / response",
        "Long-term retention",
        "Unsubscribe risk",
        "Fatigue exposure",
        "Incremental lift",
        "Rollout safety",
    ]:
        assert label in metrics
    assert "Primary metric defines success. Secondary and guardrail metrics determine whether the result is safe to expand." in metrics
    assert "Probability best estimates the chance this policy is currently the best option for the selected objective." in metrics
    assert "It does not automatically mean the policy should launch" in metrics
    assert "Why winners can differ" in metrics
    assert "Short-term winner refers to immediate" in metrics
    assert ".metric-priority-panel" in styles


def test_primary_ui_avoids_raw_lowercase_rollback_copy():
    metrics = read("frontend/src/components/MetricsCards.jsx")
    launch = read("frontend/src/components/LaunchIntelligencePanel.jsx")

    assert "Rollback Recommended" in metrics + launch
    assert "Rollback is reserved for already-expanded policies" in metrics + launch
    assert ">{rollback}<" not in metrics
    assert "rollback posture" not in metrics


def test_launch_intelligence_separates_experiment_signal_from_safety():
    launch = read("frontend/src/components/LaunchIntelligencePanel.jsx")

    assert "Experiment result:" in launch
    assert "Long-term result:" in launch
    assert "Operational recommendation:" in launch
    assert "Governance can hold expansion even when a policy is statistically promising" in launch
    assert "Expansion holds" in launch


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


def test_overview_bottom_how_to_read_section_removed():
    app = read("frontend/src/App.jsx")

    overview_block = app.split('{activeTab === "Overview" && (', 1)[1].split(
        '{activeTab === "Experimentation" && (',
        1,
    )[0]
    assert "How to read this dashboard" not in overview_block
    assert "Operational Risks" not in overview_block
    assert "Decision supported" not in overview_block
    assert "Can go wrong" not in app


def test_primary_ui_uses_professional_policy_labels():
    components = [
        "frontend/src/components/MetricsCards.jsx",
        "frontend/src/components/TradeoffPanel.jsx",
        "frontend/src/components/GovernancePanel.jsx",
        "frontend/src/components/OpePanel.jsx",
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
    assert "Epsilon Greedy" in guided
    assert "explores aggressively for short-term response" in guided


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
        "TradeoffPanel.jsx",
        "GovernancePanel.jsx",
        "OpePanel.jsx",
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


def test_lifecycle_messaging_narrative_and_intervention_catalog_render():
    app = read("frontend/src/App.jsx")
    scenario = read("frontend/src/components/DemoScenario.jsx")
    guided = read("frontend/src/components/GuidedMode.jsx")
    catalog = read("frontend/src/components/InterventionCatalogPanel.jsx")

    assert "InterventionCatalogPanel" in app
    assert "Northstar lifecycle messaging console" in scenario
    assert "fictional subscription platform" in scenario
    assert "message timing, frequency, length, personalization depth" in scenario
    assert "Primary metric" in guided
    assert "Secondary and guardrail metrics" in guided
    for goal in [
        "Onboarding completion",
        "Re-engagement",
        "Retention",
        "Churn prevention",
        "Subscription renewal",
        "Marketplace activity",
    ]:
        assert goal in catalog or goal.lower() in guided.lower()
    for intervention in [
        "Short reminder",
        "Personalized recommendation summary",
        "Weekly digest",
        "Win-back message",
        "Urgency reminder",
        "Educational onboarding tip",
    ]:
        assert intervention in catalog
    assert "Complete your setup to unlock personalized recommendations." in catalog
    assert "New recommendations matching your interests are waiting." in catalog
    assert "You have unread updates from creators you follow." in catalog


def test_selected_and_suppressed_intervention_panels_render():
    catalog = read("frontend/src/components/InterventionCatalogPanel.jsx")
    styles = read("frontend/src/styles.css")

    assert "Selected intervention" in catalog
    assert "Personalized medium-length recommendation summary" in catalog
    assert "Alternative suppressed" in catalog
    assert "High-frequency short reminder" in catalog
    assert "Reason" in catalog
    assert "Reason suppressed" in catalog
    assert "Elevated unsubscribe probability" in catalog or "elevated unsubscribe probability" in catalog
    assert "Expected tradeoff" in catalog
    assert "label-value-stack" in catalog
    assert ".label-value-stack" in styles
    for metadata in [
        "Length",
        "Personalization",
        "Frequency",
        "Fatigue",
        "Unsubscribe risk",
        "Tone",
    ]:
        assert metadata in catalog


def test_selected_suppressed_and_convergence_labels_are_not_jammed():
    catalog = read("frontend/src/components/InterventionCatalogPanel.jsx")
    convergence = read("frontend/src/components/ConvergenceMonitoringPanel.jsx")
    message = read("frontend/src/components/MessageExperimentationPanel.jsx")
    styles = read("frontend/src/styles.css")

    assert "<span>Selected intervention</span>" in catalog
    assert "<strong>Personalized medium-length recommendation summary</strong>" in catalog
    assert "<span>Alternative suppressed</span>" in catalog
    assert "<strong>High-frequency short reminder</strong>" in catalog
    assert "Selected interventionPersonalized" not in catalog
    assert "Alternative suppressedHigh-frequency" not in catalog
    assert "Policy volatilityStable" not in convergence
    assert "Recommendation stabilityNeeds Review" not in convergence
    for label in [
        "Current winning style",
        "Fatigue-safe style",
        "Highest incremental style",
        "Policy volatility",
        "Recommendation stability",
        "Reward drift",
        "Exploration concentration",
        "Arm/intervention saturation",
        "Recent change rate",
    ]:
        assert label in message + convergence
    assert "signal-status" in convergence
    assert ".signal-status" in styles


def test_ai_assisted_message_experimentation_is_constrained():
    app = read("frontend/src/App.jsx")
    panel = read("frontend/src/components/MessageExperimentationPanel.jsx")
    messaging = read("frontend/src/components/MessagingGenerationPanel.jsx")

    assert "MessageExperimentationPanel" in app
    assert "Message experimentation" in panel
    assert "approved templates" in panel
    assert "review-only" in panel.lower()
    assert "does not generate arbitrary copy" in panel
    assert "Message length" in panel
    assert "Personalization depth" in panel
    assert "Cadence" in panel
    assert "Urgency level" in panel
    assert "Short reminders maximize immediate clicks but increase fatigue risk." in panel
    assert "Personalized summaries reduce short-term CTR but improve long-term retention." in panel
    assert "High-frequency interventions show elevated unsubscribe risk" in panel
    assert "unrestricted" not in messaging.lower()


def test_policy_intervention_examples_are_pm_readable():
    panel = read("frontend/src/components/ExperimentComparisonPanel.jsx")

    assert "LinUCB" in panel
    assert "Personalizes message choices using user context and longer-term behavioral patterns." in panel
    assert "Epsilon Greedy" in panel
    assert "explores aggressively" in panel.lower()
    assert "Thompson Sampling" in panel
    assert "Balances learning and performance by favoring options that look promising but still have uncertainty." in panel
    assert "Static A/B Control" in panel
    assert "baseline comparison" in panel


def test_decision_trace_and_system_flow_render():
    app = read("frontend/src/App.jsx")
    trace = read("frontend/src/components/DecisionTracePanel.jsx")
    flow = read("frontend/src/components/SystemFlowPanel.jsx")

    assert "DecisionTracePanel" in app
    assert "SystemFlowPanel" in app
    assert "Decision Trace" in trace
    for field in [
        "User/context features",
        "Eligible intervention candidates",
        "Selected intervention/message",
        "Selection probability",
        "Expected immediate reward",
        "Expected long-term reward",
        "Observed reward",
        "Fatigue impact",
        "Unsubscribe impact",
        "Governance checks applied",
        "Final recommendation/logged outcome",
    ]:
        assert field in trace
    for step in [
        "User context",
        "Candidate interventions",
        "Policy selection",
        "Decision logging",
        "Reward ingestion",
        "Metrics summary",
        "OPE/uplift evaluation",
        "Governance checks",
        "Rollout recommendation",
    ]:
        assert step in flow


def test_decision_trace_uses_realistic_intervention_metadata():
    trace = read("frontend/src/components/DecisionTracePanel.jsx")

    assert "Personalized recommendation summary" in trace
    assert "Urgency reminder" in trace
    assert "High-frequency short reminder" in trace
    assert "message_length" in trace
    assert "tone" in trace
    assert "topic_family" in trace
    assert "fatigue" in trace.lower()
    assert "unsubscribe" in trace.lower()
    assert "whySelected" in trace


def test_convergence_status_helper_and_panel_render():
    helpers = read("frontend/src/interpretations.js")
    panel = read("frontend/src/components/ConvergenceMonitoringPanel.jsx")
    app = read("frontend/src/App.jsx")

    assert "convergenceStatus" in helpers
    for status in ["Stable", "Learning", "Volatile", "Saturated", "Needs Review"]:
        assert status in helpers or status in panel
    for signal in [
        "Policy volatility",
        "Recommendation stability",
        "Reward drift",
        "Exploration concentration",
        "Arm/intervention saturation",
        "Recent change rate",
    ]:
        assert signal in panel
    assert "ConvergenceMonitoringPanel" in app


def test_pm_experiment_comparison_and_adaptive_grounding_render():
    app = read("frontend/src/App.jsx")
    panel = read("frontend/src/components/ExperimentComparisonPanel.jsx")
    loading = read("frontend/src/components/LoadingState.jsx")

    assert "ExperimentComparisonPanel" in app
    assert "What strategies are being tested?" in panel
    assert "Northstar is comparing a traditional static A/B baseline against three adaptive policies that learn from traffic over time." in panel
    assert "Static A/B Control" in panel
    assert "Traditional equal-split experiment used as the baseline comparison." in panel
    assert "Explores aggressively and quickly shifts toward messages that get short-term engagement." in panel
    assert "Balances learning and performance by favoring options that look promising but still have uncertainty." in panel
    assert "Personalizes message choices using user context and longer-term behavioral patterns." in panel
    assert "What is this system?" in loading
    assert "Northstar" in loading
    assert "long-term fatigue" in loading


def test_strategy_setup_precedes_pm_decision_and_has_no_jammed_labels():
    app = read("frontend/src/App.jsx")
    panel = read("frontend/src/components/ExperimentComparisonPanel.jsx")
    styles = read("frontend/src/styles.css")
    overview_block = app.split('{activeTab === "Overview" && (', 1)[1].split(
        '{activeTab === "Experimentation" && (',
        1,
    )[0]

    assert overview_block.index("ExperimentComparisonPanel") < overview_block.index("MetricsCards")
    assert "strategy-card-heading" in panel
    assert ".strategy-card-heading" in styles
    for label in [
        "Static A/B Control",
        "Epsilon Greedy",
        "Thompson Sampling",
        "LinUCB",
    ]:
        assert label in panel
    assert "LinUCBAdaptive" not in panel
    assert "Epsilon GreedyAdaptive" not in panel
    assert "Thompson SamplingAdaptive" not in panel


def test_strategy_legend_is_compact_and_contains_no_metrics_or_recommendations():
    panel = read("frontend/src/components/ExperimentComparisonPanel.jsx")
    app = read("frontend/src/App.jsx")
    overview_block = app.split('{activeTab === "Overview" && (', 1)[1].split(
        '{activeTab === "Experimentation" && (',
        1,
    )[0]

    assert overview_block.index("ExperimentComparisonPanel") < overview_block.index("MetricsCards")
    for description in [
        "Traditional equal-split experiment used as the baseline comparison.",
        "Explores aggressively and quickly shifts toward messages that get short-term engagement.",
        "Balances learning and performance by favoring options that look promising but still have uncertainty.",
        "Personalizes message choices using user context and longer-term behavioral patterns.",
    ]:
        assert description in panel

    for removed in [
        "Click/engagement outcome",
        "Long-term retention outcome",
        "Unsubscribe/fatigue risk",
        "Confidence",
        "Rollout posture",
        "Recommendation",
        "average_reward",
        "probability_best",
        "launchRecommendation",
        "statisticalPosture",
        "launch-badge",
        "<dl",
        "<dt",
        "<dd",
        "Why adaptive experimentation?",
        "Traditional A/B tests keep traffic fixed.",
    ]:
        assert removed not in panel


def test_no_duplicate_ope_governance_panels_between_tabs():
    app = read("frontend/src/App.jsx")
    experimentation_block = app.split('{activeTab === "Experimentation" && (', 1)[1].split(
        '{activeTab === "Risk & Governance" && (',
        1,
    )[0]
    governance_block = app.split('{activeTab === "Risk & Governance" && (', 1)[1].split(
        '{activeTab === "Live Operations" && (',
        1,
    )[0]

    assert "OpePanel" in experimentation_block
    assert "GovernancePanel" not in experimentation_block
    assert "GovernancePanel" in governance_block
    assert "OpePanel" not in governance_block
    assert "Off-policy evaluation" in read("frontend/src/components/OpePanel.jsx")
    assert "Governance recommendations" in read("frontend/src/components/GovernancePanel.jsx")


def test_ai_tab_focuses_on_intervention_review_not_policy_strategy_cards():
    app = read("frontend/src/App.jsx")
    message_panel = read("frontend/src/components/MessageExperimentationPanel.jsx")
    ai_block = app.split('{activeTab === "AI & Decision Support" && (', 1)[1]

    assert "This tab explains how the system chooses and reviews specific message interventions." in app
    assert "AssignmentPanel" in ai_block
    assert "MessageExperimentationPanel" in ai_block
    assert "MessagingGenerationPanel" in ai_block
    assert "policy-examples" not in message_panel
    assert "Static Control" not in message_panel
    assert "Thompson Sampling" not in message_panel


def test_primary_ui_avoids_raw_status_labels_and_awkward_copy():
    components = [
        read("frontend/src/components/GovernancePanel.jsx"),
        read("frontend/src/components/DecisionLogPanel.jsx"),
        read("frontend/src/components/ExperimentComparisonPanel.jsx"),
        read("frontend/src/components/PolicyLifecyclePanel.jsx"),
    ]
    joined = "\n".join(components)

    assert "Continue Rollout" in joined
    assert "Human Review" in joined
    assert "Hold Expansion" in joined
    assert "Rollback Recommended" in joined
    assert "most experimentation dashboards stop at" not in joined
    assert ">deploy<" not in joined
    assert ">human_review<" not in joined
    assert ">hold_expansion<" not in joined
