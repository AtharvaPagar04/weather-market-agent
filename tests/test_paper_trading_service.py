from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import MarketSnapshot, PaperOrder, RiskReport
from app.services.city_service import CityService
from app.services.market_service import MarketService
from app.services.paper_trading_service import PaperTradingService
from app.services.prediction_service import PredictionService
from app.services.risk_service import RiskService
from app.services.weather_service import WeatherService
from app.tools.apify_weather_tool import ApifyWeatherTool
from app.tools.global_weather_tool import GlobalWeatherTool
from app.tools.local_weather_tool import LocalWeatherTool


class CountingPaperTool:
    def __init__(self) -> None:
        self.calls = 0

    def paper_buy(self, **kwargs) -> dict:
        self.calls += 1
        return {"success": False, "status": "paper_execution_disabled"}


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'paper_trading_service.db'}"
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
    RiskService().analyze_risk(db)


def test_run_paper_trading_creates_one_decision_per_city(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)

        result = PaperTradingService().run_paper_trading(db)

        assert result["success"] is True
        assert result["cities_processed"] == 5
        assert result["paper_orders_created"] + result["paper_orders_skipped"] == 5
        assert db.query(PaperOrder).count() == 5
    finally:
        db.close()


def test_created_orders_match_approved_risk_reports(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)

        PaperTradingService().run_paper_trading(db)

        approved_count = db.query(RiskReport).filter(RiskReport.trade_allowed.is_(True)).count()
        created_count = db.query(PaperOrder).filter(PaperOrder.status == "paper_order_created").count()
        assert created_count == approved_count
    finally:
        db.close()


def test_blocked_risk_report_creates_skipped_order_without_pm_call(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    paper_tool = CountingPaperTool()
    try:
        _prepare_inputs(db)
        risk_report = db.query(RiskReport).first()
        risk_report.trade_allowed = False
        risk_report.blocked_reason = "test_blocked"
        db.commit()

        PaperTradingService(paper_trade_tool=paper_tool).run_paper_trading(db, city_ids=[risk_report.city_id])

        order = db.query(PaperOrder).filter(PaperOrder.risk_report_id == risk_report.id).first()
        assert order.status == "paper_order_skipped"
        assert order.side == "NONE"
        assert paper_tool.calls == 0
    finally:
        db.close()


def test_duplicate_run_does_not_duplicate_orders_for_same_risk_report(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)
        service = PaperTradingService()
        service.run_paper_trading(db)

        second_result = service.run_paper_trading(db)

        assert db.query(PaperOrder).count() == 5
        assert second_result["paper_orders_created"] == 0
        assert second_result["paper_orders_skipped"] == 5
    finally:
        db.close()


def test_dry_run_does_not_persist_orders(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)

        result = PaperTradingService().run_paper_trading(db, dry_run=True)

        assert result["paper_orders_created"] + result["paper_orders_skipped"] == 5
        assert db.query(PaperOrder).count() == 0
    finally:
        db.close()


def test_positions_update_only_for_created_orders(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        _prepare_inputs(db)
        risk_report = db.query(RiskReport).first()
        risk_report.trade_allowed = False
        risk_report.blocked_reason = "test_blocked"
        db.commit()

        result = PaperTradingService().run_paper_trading(db)

        created_count = db.query(PaperOrder).filter(PaperOrder.status == "paper_order_created").count()
        assert result["positions_updated"] == created_count
    finally:
        db.close()
