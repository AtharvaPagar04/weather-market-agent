from app.services.evaluation_service import EvaluationService
from app.models.db_models import Prediction, RiskReport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import database
from app.services.agent_orchestration_service import AgentOrchestrationService

def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'evaluation_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()

def test_evaluation_summary_empty_db(tmp_path, monkeypatch):
    db_session = _session(tmp_path, monkeypatch)
    try:
        service = EvaluationService(db_session)
        summary = service.get_summary()
        
        assert summary["predictions_count"] == 0
        assert summary["cities_evaluated"] == 0
        assert summary["average_model_probability"] == 0
        assert summary["average_market_probability"] == 0
        assert summary["outcome_data_available"] is False
        assert summary["accuracy_metrics_available"] is False
        assert "Realized weather outcomes are not available" in summary["message"]
    finally:
        db_session.close()

def test_evaluation_summary_with_data(tmp_path, monkeypatch):
    db_session = _session(tmp_path, monkeypatch)
    try:
        # Seed data
        from app.services.city_service import CityService
        CityService.seed_default_cities(db_session)
        p = Prediction(city_id=1, model_probability=0.5, market_probability=0.4, raw_edge=0.1, confidence_score=0.8, model_version="1.0", prediction_label="YES", prediction_type="binary")
        db_session.add(p)
        db_session.flush() # get p.id
        
        r = RiskReport(
            city_id=1, 
            prediction_id=p.id, 
            market_slug="market-1",
            model_probability=0.5, 
            market_probability=0.4, 
            raw_edge=0.1, 
            tradeable_edge=0.08, 
            confidence=0.8, 
            risk_level="LOW", 
            risk_decision="PAPER_TRADE_NORMAL", 
            trade_allowed=True, 
            recommended_size=10
        )
        db_session.add(r)
        db_session.commit()
        
        service = EvaluationService(db_session)
        summary = service.get_summary()
        
        assert summary["predictions_count"] == 1
        assert summary["cities_evaluated"] == 1
        assert summary["average_model_probability"] == 0.5
        assert summary["average_market_probability"] == 0.4
        assert summary["average_raw_edge"] == 0.1
        assert summary["average_confidence"] == 0.8
        assert summary["trade_allowed_count"] == 1
    finally:
        db_session.close()


def test_evaluation_summary_after_real_agent_run(tmp_path, monkeypatch):
    db_session = _session(tmp_path, monkeypatch)
    try:
        AgentOrchestrationService().run_full_pipeline(db=db_session)

        summary = EvaluationService(db_session).get_summary()

        assert summary["predictions_count"] > 0
        assert summary["cities_evaluated"] > 0
        assert summary["risk_reports_count"] > 0
        assert summary["market_snapshots_count"] > 0
        assert summary["weather_snapshots_count"] > 0
        assert summary["agent_runs_count"] > 0
        assert summary["latest_agent_status"] in {"completed", "partial"}
        assert summary["paper_orders_skipped"] >= 0
        assert summary["watch_decision_count"] >= 0
        assert summary["outcome_data_available"] is False
        assert summary["accuracy_metrics_available"] is False
    finally:
        db_session.close()
