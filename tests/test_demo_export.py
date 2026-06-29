import os
import json
import csv
from app.services.evaluation_service import EvaluationService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import database
from app.services.agent_orchestration_service import AgentOrchestrationService

def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'demo_export.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()

def test_demo_export_creates_files(tmp_path, monkeypatch):
    db_session = _session(tmp_path, monkeypatch)
    try:
        service = EvaluationService(db_session)
        output_dir = str(tmp_path / "demo_output")
    
        res = service.export_demo_output(output_dir=output_dir)
        assert res["status"] == "success"
        
        # Check files exist
        assert os.path.exists(os.path.join(output_dir, "results_summary.csv"))
        assert os.path.exists(os.path.join(output_dir, "sample_predictions.json"))
        assert os.path.exists(os.path.join(output_dir, "sample_orders.json"))
        assert os.path.exists(os.path.join(output_dir, "pm_trader_stats.json"))
        
        # Validate JSON
        with open(os.path.join(output_dir, "pm_trader_stats.json"), "r") as f:
            data = json.load(f)
            assert data["pm_trader_available"] is False
            assert data["readonly_mode"] is True
            assert data["order_execution_enabled"] is False
            
        # Validate CSV
        with open(os.path.join(output_dir, "results_summary.csv"), "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["paper_trading_only"] == "True"
            assert rows[0]["simulated_results"] == "True"
    finally:
        db_session.close()


def test_demo_export_after_real_agent_run_contains_populated_outputs(tmp_path, monkeypatch):
    db_session = _session(tmp_path, monkeypatch)
    output_dir = str(tmp_path / "demo_output")
    try:
        AgentOrchestrationService().run_full_pipeline(db=db_session)

        res = EvaluationService(db_session).export_demo_output(output_dir=output_dir)

        assert res["status"] == "success"
        expected_files = {
            "results_summary.csv",
            "sample_predictions.json",
            "sample_orders.json",
            "pm_trader_stats.json",
        }
        assert expected_files == {os.path.basename(path) for path in res["files_created"]}

        for file_name in expected_files:
            assert os.path.exists(os.path.join(output_dir, file_name))

        with open(os.path.join(output_dir, "results_summary.csv"), "r") as f:
            csv_text = f.read()
            assert "paper_trading_only" in csv_text
            assert "simulated_results" in csv_text
            assert "demo_results" in csv_text
            f.seek(0)
            rows = list(csv.DictReader(f))
            assert int(rows[0]["predictions_count"]) > 0
            assert int(rows[0]["agent_runs_count"]) > 0

        with open(os.path.join(output_dir, "sample_predictions.json"), "r") as f:
            predictions = json.load(f)
            assert predictions
            assert all(item["paper_trading_only"] is True for item in predictions)

        with open(os.path.join(output_dir, "sample_orders.json"), "r") as f:
            orders = json.load(f)
            assert orders
            assert all(item["paper_status"].startswith("paper_") for item in orders)
            assert all(item["simulated_results"] is True for item in orders)

        with open(os.path.join(output_dir, "pm_trader_stats.json"), "r") as f:
            stats = json.load(f)
            assert stats["readonly_mode"] is True
            assert stats["order_execution_enabled"] is False
    finally:
        db_session.close()
