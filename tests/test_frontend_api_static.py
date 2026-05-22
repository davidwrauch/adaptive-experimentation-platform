from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_api_helpers_include_persistent_control_update():
    api = (ROOT / "frontend/src/api.js").read_text(encoding="utf-8")

    assert "export function updatePolicyControl" in api
    assert 'method: "POST"' in api
    assert "/controls/policies/" in api
