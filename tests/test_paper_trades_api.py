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

    test_db_url = f"sqlite:///{tmp_path / 'paper_trades_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def _run_pipeline(client: TestClient) -> None:
    assert client.post("/cities/seed", json={"reset_existing": False}).status_code == 200
    assert client.post("/weather/refresh", json={"sources": ["global", "local", "apify"], "use_mock_on_failure": True}).status_code == 200
    assert client.post("/markets/refresh", json={"force_mock": False, "use_mock_if_unavailable": True}).status_code == 200
    assert client.post("/predictions/run", json={"model_version": "baseline_v1"}).status_code == 200
    assert client.post("/risk/analyze", json={"bankroll": 1000.0}).status_code == 200


def test_paper_trading_run_and_list_orders(client: TestClient) -> None:
    _run_pipeline(client)

    run_response = client.post("/paper-trades/run", json={"dry_run": False})

    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["paper_orders_created"] + run_payload["paper_orders_skipped"] == 5

    orders_response = client.get("/paper-trades")
    orders_payload = orders_response.json()

    assert orders_response.status_code == 200
    assert len(orders_payload) == 5
    assert all(order["status"].startswith("paper_") for order in orders_payload)


def test_no_real_order_routes_exist() -> None:
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
