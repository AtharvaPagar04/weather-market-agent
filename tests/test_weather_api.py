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

    test_db_url = f"sqlite:///{tmp_path / 'weather_api.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_weather_refresh_and_latest_endpoints(client: TestClient) -> None:
    seed_response = client.post("/cities/seed", json={"reset_existing": False})
    assert seed_response.status_code == 200

    refresh_response = client.post(
        "/weather/refresh",
        json={"sources": ["global", "local", "apify"], "use_mock_on_failure": True},
    )

    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    assert refresh_payload["success"] is True
    assert refresh_payload["snapshots_created"] == 15
    assert refresh_payload["snapshots_created"] >= 10
    assert any(failure["source"] == "apify" for failure in refresh_payload["failed_sources"])

    latest_response = client.get("/weather/latest")

    assert latest_response.status_code == 200
    latest_payload = latest_response.json()
    assert latest_payload
    assert {"city_id", "source", "status", "rain_probability", "temperature_c", "humidity_pct", "created_at"}.issubset(
        latest_payload[0]
    )
