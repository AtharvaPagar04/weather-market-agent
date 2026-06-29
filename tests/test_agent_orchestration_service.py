import inspect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.models.db_models import AgentRun, AgentRunLog, PaperOrder
from app.services.agent_orchestration_service import AgentOrchestrationService


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'agent_orchestration_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()


def test_run_full_pipeline_from_empty_db_creates_run_logs_and_outputs(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        result = AgentOrchestrationService().run_full_pipeline(db=db)

        assert result["success"] is True
        assert result["status"] in {"completed", "partial"}
        assert result["agent_run_id"] is not None
        assert result["cities_processed"] == 5
        assert result["weather_snapshots_created"] == 15
        assert result["market_snapshots_created"] == 5
        assert result["predictions_created"] == 5
        assert result["risk_reports_created"] == 5
        assert result["paper_orders_created"] + result["paper_orders_skipped"] == 5
        assert len(result["summary"]) == 5
        assert db.query(AgentRun).count() == 1
        assert db.query(AgentRunLog).count() >= 6
        assert db.query(PaperOrder).count() == 5
    finally:
        db.close()


class RecordingPaperTradingService:
    def __init__(self) -> None:
        self.called = False
        self.city_ids = None

    def run_paper_trading(self, db, city_ids=None, dry_run: bool = False) -> dict:
        self.called = True
        self.city_ids = city_ids
        return {
            "success": True,
            "cities_processed": len(city_ids or []),
            "paper_orders_created": 0,
            "paper_orders_skipped": len(city_ids or []),
            "positions_updated": 0,
            "failed_paper_orders": [],
        }


def test_orchestration_uses_paper_trading_service_boundary(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    paper_service = RecordingPaperTradingService()
    try:
        result = AgentOrchestrationService(paper_trading_service=paper_service).run_full_pipeline(db=db)

        assert result["success"] is True
        assert paper_service.called is True
        assert len(paper_service.city_ids) == 5
    finally:
        db.close()


def test_orchestration_does_not_call_pm_trader_paper_methods_directly() -> None:
    source = inspect.getsource(AgentOrchestrationService)

    assert ".paper_buy(" not in source
    assert ".paper_sell(" not in source
