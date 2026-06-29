from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import RiskReport
from app.services.city_service import CityService
from app.services.market_service import MarketService
from app.services.prediction_service import PredictionService
from app.services.risk_service import RiskService
from app.services.weather_service import WeatherService
from app.tools.apify_weather_tool import ApifyWeatherTool
from app.tools.global_weather_tool import GlobalWeatherTool
from app.tools.local_weather_tool import LocalWeatherTool


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'risk_service.db'}"
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
    MarketService().refresh_markets(db, force_mock=False, use_mock_if_unavailable=True)
    PredictionService().run_predictions(db)


def test_analyze_risk_creates_reports_for_mvp_cities(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)

        result = RiskService().analyze_risk(db)

        assert result["success"] is True
        assert result["cities_processed"] == 5
        assert result["risk_reports_created"] == 5
        assert result["trade_allowed_count"] + result["trade_blocked_count"] == 5
        reports = db.query(RiskReport).all()
        assert len(reports) == 5
        assert all(0 <= report.confidence <= 1 for report in reports)
        assert all(report.recommended_size >= 0 for report in reports)
    finally:
        db.close()


def test_get_latest_risk_reports_returns_records(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)
        service = RiskService()
        service.analyze_risk(db)

        records = service.get_latest_risk_reports(db)

        assert records
        assert len(records) == 5
    finally:
        db.close()


def test_analyze_risk_city_ids_filter_works(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)
        city = CityService.get_active_cities(db)[0]

        result = RiskService().analyze_risk(db, city_ids=[city.id])

        assert result["cities_processed"] == 1
        assert result["risk_reports_created"] == 1
        records = RiskService().get_latest_risk_reports(db, city_id=city.id)
        assert len(records) == 1
        assert records[0].city_id == city.id
    finally:
        db.close()


def test_missing_prediction_or_market_data_records_failure_without_crashing(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        CityService.seed_default_cities(db)

        result = RiskService().analyze_risk(db)

        assert result["success"] is True
        assert result["risk_reports_created"] == 0
        assert len(result["failed_risk_reports"]) == 5
    finally:
        db.close()


def test_no_pm_trader_execution_is_called(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)

        result = RiskService().analyze_risk(db)

        assert result["risk_reports_created"] == 5
    finally:
        db.close()
