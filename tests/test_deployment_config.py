from pathlib import Path

from app.main import health


ROOT = Path(__file__).resolve().parents[1]


def test_env_examples_exist_and_include_required_vars():
    backend_env = (ROOT / "backend/.env.example").read_text(encoding="utf-8")
    frontend_env = (ROOT / "frontend/.env.example").read_text(encoding="utf-8")

    assert "DATABASE_URL=" in backend_env
    assert "CORS_ORIGINS=" in backend_env
    assert "AUTO_CREATE_TABLES=" in backend_env
    assert "VITE_API_BASE=" in frontend_env


def test_render_and_vercel_configs_exist():
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    vercel = (ROOT / "frontend/vercel.json").read_text(encoding="utf-8")

    assert "uvicorn app.main:app" in render
    assert "DATABASE_URL" in render
    assert '"outputDirectory": "dist"' in vercel


def test_health_endpoint_includes_status():
    body = health()

    assert body["status"] == "ok"
    assert "environment" in body
