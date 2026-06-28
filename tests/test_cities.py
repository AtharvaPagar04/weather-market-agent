from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    test_db_url = f"sqlite:///{tmp_path / 'cities.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    with TestClient(app) as test_client:
        yield test_client


def test_seed_cities_creates_default_cities(client: TestClient) -> None:
    response = client.post("/cities/seed", json={"reset_existing": False})

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Default cities seeded successfully.",
        "cities_created": 5,
        "total_active_cities": 5,
    }


def test_get_cities_returns_seeded_active_cities(client: TestClient) -> None:
    client.post("/cities/seed", json={"reset_existing": False})

    response = client.get("/cities")

    assert response.status_code == 200
    cities = response.json()
    assert len(cities) == 5
    assert {city["name"] for city in cities} == {"Mumbai", "London", "New York", "Tokyo", "Sydney"}
    assert all(city["is_active"] for city in cities)


def test_seed_cities_is_idempotent_without_reset(client: TestClient) -> None:
    client.post("/cities/seed", json={"reset_existing": False})

    response = client.post("/cities/seed", json={"reset_existing": False})

    assert response.status_code == 200
    assert response.json()["cities_created"] == 0
    assert response.json()["total_active_cities"] == 5
    assert response.json()["message"] == "Default cities already available."


def test_seed_cities_with_reset_keeps_exactly_five_active_cities(client: TestClient) -> None:
    client.post("/cities/seed", json={"reset_existing": False})

    response = client.post("/cities/seed", json={"reset_existing": True})

    assert response.status_code == 200
    assert response.json()["cities_created"] == 5
    assert response.json()["total_active_cities"] == 5

    cities_response = client.get("/cities")
    assert cities_response.status_code == 200
    assert len(cities_response.json()) == 5
