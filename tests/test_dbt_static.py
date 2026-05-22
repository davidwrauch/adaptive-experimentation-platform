from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DBT = ROOT / "dbt"


def test_dbt_files_exist():
    expected = [
        "dbt_project.yml",
        "models/staging/stg_events.sql",
        "models/staging/stg_assignments.sql",
        "models/marts/mart_policy_performance.sql",
        "models/marts/mart_experiment_health.sql",
        "models/marts/mart_user_state.sql",
        "models/marts/mart_governance_decisions.sql",
        "models/schema.yml",
        "README.md",
    ]

    for relative_path in expected:
        assert (DBT / relative_path).exists()


def test_expected_model_names_exist_in_schema():
    schema = (DBT / "models/schema.yml").read_text(encoding="utf-8")

    for model in [
        "stg_events",
        "stg_assignments",
        "mart_policy_performance",
        "mart_experiment_health",
        "mart_user_state",
        "mart_governance_decisions",
    ]:
        assert f"name: {model}" in schema


def test_policy_performance_sql_contains_required_columns():
    sql = (DBT / "models/marts/mart_policy_performance.sql").read_text(encoding="utf-8")

    for column in [
        "policy",
        "event_count",
        "average_immediate_reward",
        "average_long_term_reward",
        "cumulative_immediate_reward",
        "cumulative_long_term_reward",
    ]:
        assert column in sql


def test_governance_sql_contains_status_and_reason():
    sql = (DBT / "models/marts/mart_governance_decisions.sql").read_text(encoding="utf-8")

    assert "governance_status" in sql
    assert "governance_reason" in sql


def test_lifecycle_messaging_docs_exist():
    docs = ROOT / "docs/lifecycle_messaging_scenario.md"
    readme = ROOT / "README.md"
    content = docs.read_text(encoding="utf-8")
    readme_content = readme.read_text(encoding="utf-8")

    assert "Northstar" in content
    assert "subscription-based platform" in content
    assert "short reminder" in content
    assert "personalized recommendation summary" in content
    assert "Hold Expansion" in content
    assert "Constrained AI Messaging" in content
    assert "Lifecycle messaging scenario" in readme_content
