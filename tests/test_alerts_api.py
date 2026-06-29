from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.config import get_settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("TELEGRAM_ALERTS_ENABLED", "false")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "")
    monkeypatch.setenv("APIFY_API_TOKEN", "")
    get_settings.cache_clear()

    test_db_url = f"sqlite:///{tmp_path / 'alerts_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_alert_status_does_not_expose_token(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_ALERTS_ENABLED", "true")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "secret-token-value")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    get_settings.cache_clear()

    response = client.get("/alerts/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is True
    assert payload["configured"] is True
    assert payload["token_configured"] is True
    assert "secret-token-value" not in response.text


def test_disabled_test_alert_returns_skipped(client: TestClient) -> None:
    response = client.post("/alerts/test", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["sent"] is False
    assert payload["skipped"] is True
    assert payload["reason"] == "telegram alerts disabled"
    assert "Paper trading only" in payload["message"]


def test_latest_run_alert_works_without_agent_run(client: TestClient) -> None:
    response = client.post("/alerts/latest-run", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["skipped"] is True
    assert "Status: no_agent_run" in payload["message"]
    assert "simulated execution" in payload["message"]


def test_latest_run_alert_after_agent_pipeline(client: TestClient) -> None:
    agent_response = client.post("/agent/run", json={})
    assert agent_response.status_code == 200

    response = client.post("/alerts/latest-run", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["sent"] is False
    assert payload["skipped"] is True
    assert "Cities processed: 5" in payload["message"]
    assert "Predictions: 5" in payload["message"]
    assert "Paper orders skipped:" in payload["message"]
    assert "Paper trading only" in payload["message"]
