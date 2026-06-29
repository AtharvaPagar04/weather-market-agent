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

    test_db_url = f"sqlite:///{tmp_path / 'agent_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_agent_run_and_log_endpoints(client: TestClient) -> None:
    run_response = client.post(
        "/agent/run",
        json={"force_mock_markets": False, "run_evaluation_after": False},
    )

    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["agent_run_id"] is not None
    assert run_payload["weather_snapshots_created"] == 15
    assert run_payload["market_snapshots_created"] == 5
    assert run_payload["predictions_created"] == 5
    assert run_payload["risk_reports_created"] == 5
    assert run_payload["paper_orders_created"] + run_payload["paper_orders_skipped"] == 5

    runs_response = client.get("/agent/runs")
    logs_response = client.get("/agent/logs")

    assert runs_response.status_code == 200
    assert logs_response.status_code == 200
    assert len(runs_response.json()) >= 1
    assert len(logs_response.json()) >= 6


def test_no_real_execution_routes_exist() -> None:
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    blocked_paths = {
        "/orders" + "/place",
        "/trade" + "/execute",
        "/account" + "/connect",
        "/private" + "-key",
        "/wal" + "let",
        "/paper-trader/buy",
        "/paper-trader/sell",
        "/paper-trader/order",
    }

    for blocked in blocked_paths:
        assert blocked not in paths
