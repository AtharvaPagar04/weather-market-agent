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
    monkeypatch.setenv("APIFY_API_TOKEN", "")
    get_settings.cache_clear()

    test_db_url = f"sqlite:///{tmp_path / 'evaluation_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_get_evaluation_summary_empty_db(client: TestClient):
    response = client.get("/evaluation/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["predictions_count"] == 0
    assert data["outcome_data_available"] is False
    assert data["accuracy_metrics_available"] is False


def test_populated_evaluation_summary_after_agent_run(client: TestClient):
    agent_response = client.post("/agent/run", json={})
    assert agent_response.status_code == 200

    response = client.get("/evaluation/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["predictions_count"] > 0
    assert data["cities_evaluated"] > 0
    assert data["risk_reports_count"] > 0
    assert data["market_snapshots_count"] > 0
    assert data["weather_snapshots_count"] > 0
    assert data["agent_runs_count"] > 0
    assert data["paper_orders_skipped"] >= 0
    assert data["outcome_data_available"] is False
    assert data["accuracy_metrics_available"] is False


def test_post_evaluation_run_after_agent_run(client: TestClient):
    assert client.post("/agent/run", json={}).status_code == 200

    response = client.post("/evaluation/run")
    assert response.status_code == 200
    data = response.json()
    assert "predictions_count" in data
    assert data["accuracy_metrics_available"] is False


def test_post_demo_export_after_agent_run(client: TestClient):
    assert client.post("/agent/run", json={}).status_code == 200

    response = client.post("/demo/export")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "files_created" in data
    assert len(data["files_created"]) == 4
