from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    test_db_url = f"sqlite:///{tmp_path / 'market_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client


def test_market_refresh_and_get_markets_endpoints(client: TestClient) -> None:
    seed_response = client.post("/cities/seed", json={"reset_existing": False})
    assert seed_response.status_code == 200

    refresh_response = client.post(
        "/markets/refresh",
        json={"force_mock": True, "use_mock_if_unavailable": True},
    )

    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    assert refresh_payload["success"] is True
    assert refresh_payload["market_snapshots_created"] == 5

    markets_response = client.get("/markets")

    assert markets_response.status_code == 200
    markets_payload = markets_response.json()
    assert len(markets_payload) == 5
    assert all(market["source_type"] == "mock" for market in markets_payload)
    assert all(market["market_slug"] for market in markets_payload)
