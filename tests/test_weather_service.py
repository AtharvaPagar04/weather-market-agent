from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import WeatherSnapshot
from app.services.city_service import CityService
from app.services.weather_service import WeatherService
from app.tools.apify_weather_tool import ApifyWeatherTool
from app.tools.global_weather_tool import GlobalWeatherTool
from app.tools.local_weather_tool import LocalWeatherTool


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'weather_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()


def _weather_service() -> WeatherService:
    return WeatherService(
        tools={
            "global": GlobalWeatherTool(),
            "local": LocalWeatherTool(),
            "apify": ApifyWeatherTool(api_token=""),
        }
    )


def test_refresh_weather_creates_snapshots_for_default_sources(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)

        result = _weather_service().refresh_weather(db)

        assert result["success"] is True
        assert result["cities_processed"] == 5
        assert result["snapshots_created"] == 15
        assert result["sources_used"] == ["global", "local", "apify"]
        assert len(result["failed_sources"]) == 5
        assert db.query(WeatherSnapshot).count() == 15
        assert db.query(WeatherSnapshot).filter(WeatherSnapshot.source == "apify").first().status == "failed"
    finally:
        db.close()


def test_get_latest_weather_returns_records(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)
        service = _weather_service()
        service.refresh_weather(db)

        records = service.get_latest_weather(db)

        assert records
        assert len(records) == 15
    finally:
        db.close()


def test_refresh_weather_city_ids_filter_works(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)
        city = CityService.get_active_cities(db)[0]

        result = _weather_service().refresh_weather(db, city_ids=[city.id], sources=["global", "local"])

        assert result["cities_processed"] == 1
        assert result["snapshots_created"] == 2
        records = _weather_service().get_latest_weather(db, city_id=city.id)
        assert len(records) == 2
        assert {record.city_id for record in records} == {city.id}
    finally:
        db.close()
