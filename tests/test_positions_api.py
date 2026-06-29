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

    test_db_url = f"sqlite:///{tmp_path / 'positions_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_positions_endpoint_returns_simulated_positions(client: TestClient) -> None:
    client.post("/cities/seed", json={"reset_existing": False})
    client.post("/weather/refresh", json={"sources": ["global", "local", "apify"], "use_mock_on_failure": True})
    client.post("/markets/refresh", json={"force_mock": False, "use_mock_if_unavailable": True})
    client.post("/predictions/run", json={"model_version": "baseline_v1"})
    client.post("/risk/analyze", json={"bankroll": 1000.0})
    paper_response = client.post("/paper-trades/run", json={"dry_run": False})

    positions_response = client.get("/positions")

    assert positions_response.status_code == 200
    positions_payload = positions_response.json()
    assert len(positions_payload) <= paper_response.json()["paper_orders_created"]
    if positions_payload:
        position = positions_payload[0]
        assert {"side", "total_size", "average_price", "status"}.issubset(position)
