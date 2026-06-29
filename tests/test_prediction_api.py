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

    test_db_url = f"sqlite:///{tmp_path / 'prediction_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_prediction_run_and_latest_endpoints(client: TestClient) -> None:
    assert client.post("/cities/seed", json={"reset_existing": False}).status_code == 200
    assert client.post("/weather/refresh", json={"sources": ["global", "local", "apify"], "use_mock_on_failure": True}).status_code == 200
    assert client.post("/markets/refresh", json={"force_mock": False, "use_mock_if_unavailable": True}).status_code == 200

    run_response = client.post("/predictions/run", json={"model_version": "baseline_v1"})

    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["success"] is True
    assert run_payload["predictions_created"] == 5

    latest_response = client.get("/predictions/latest")

    assert latest_response.status_code == 200
    latest_payload = latest_response.json()
    assert len(latest_payload) == 5
    assert all("prediction_label" in prediction for prediction in latest_payload)


def test_no_risk_or_trading_routes_exist() -> None:
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    blocked_paths = {
        "/risk/analyze",
        "/paper-trader/buy",
        "/paper-trader/sell",
        "/paper-trader/order",
        "/paper-trades/buy",
        "/paper-trades/sell",
    }

    for blocked in blocked_paths:
        assert blocked not in paths
