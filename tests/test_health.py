import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_expected_payload() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["app_name"] == "Weather Market Agent"
    assert response.json()["environment"] == "development"
    assert response.json()["database"] == "not_checked"


def test_importing_app_main_does_not_initialize_database(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    module = importlib.import_module("app.main")
    importlib.reload(module)

    assert module.app is not None
    assert not Path("weather_agent.db").exists()

