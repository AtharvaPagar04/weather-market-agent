from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import Prediction
from app.services.city_service import CityService
from app.services.market_service import MarketService
from app.services.prediction_service import PredictionService
from app.services.weather_service import WeatherService
from app.tools.apify_weather_tool import ApifyWeatherTool
from app.tools.global_weather_tool import GlobalWeatherTool
from app.tools.local_weather_tool import LocalWeatherTool


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'prediction_service.db'}"
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


def _prepare_inputs(db) -> None:
    CityService.seed_default_cities(db)
    _weather_service().refresh_weather(db)
    MarketService().refresh_markets(db)


def test_run_predictions_creates_predictions_for_mvp_cities(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)

        result = PredictionService().run_predictions(db)

        assert result == {
            "success": True,
            "cities_processed": 5,
            "predictions_created": 5,
            "model_version": "baseline_v1",
            "failed_predictions": [],
        }
        predictions = db.query(Prediction).all()
        assert len(predictions) == 5
        assert all(0 <= prediction.model_probability <= 1 for prediction in predictions)
        assert all(0 <= prediction.market_probability <= 1 for prediction in predictions)
        assert all(0 <= prediction.confidence_score <= 1 for prediction in predictions)
    finally:
        db.close()


def test_get_latest_predictions_returns_records(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)
        service = PredictionService()
        service.run_predictions(db)

        records = service.get_latest_predictions(db)

        assert records
        assert len(records) == 5
    finally:
        db.close()


def test_run_predictions_city_ids_filter_works(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)
        city = CityService.get_active_cities(db)[0]

        result = PredictionService().run_predictions(db, city_ids=[city.id])

        assert result["cities_processed"] == 1
        assert result["predictions_created"] == 1
        records = PredictionService().get_latest_predictions(db, city_id=city.id)
        assert len(records) == 1
        assert records[0].city_id == city.id
    finally:
        db.close()


def test_missing_market_or_weather_records_failed_prediction_without_crashing(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)

        result = PredictionService().run_predictions(db)

        assert result["success"] is True
        assert result["predictions_created"] == 0
        assert len(result["failed_predictions"]) == 5
    finally:
        db.close()
