import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.services.agent_log_service import AgentLogService


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'agent_log_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()


def test_agent_log_service_creates_updates_and_filters_records(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    service = AgentLogService()
    try:
        agent_run = service.create_run(db=db, run_type="full_pipeline", cities_requested=5)
        log = service.add_log(
            db=db,
            agent_run_id=agent_run.id,
            step_name="weather",
            status="success",
            message="Weather refresh completed.",
            city_id=1,
            city_name="Mumbai",
            metadata={"snapshots_created": 3},
        )
        updated_run = service.update_run(
            db=db,
            agent_run=agent_run,
            status="completed",
            summary=[{"city_name": "Mumbai"}],
            counts={
                "cities_processed": 1,
                "weather_snapshots_created": 3,
                "market_snapshots_created": 1,
            },
        )

        runs = service.list_runs(db)
        completed_runs = service.list_runs(db, status="completed")
        logs = service.list_logs(db, agent_run_id=agent_run.id)
        filtered_logs = service.list_logs(db, city_id=1, status="success", step_name="weather")

        assert updated_run.status == "completed"
        assert updated_run.finished_at is not None
        assert len(runs) == 1
        assert len(completed_runs) == 1
        assert len(logs) == 1
        assert len(filtered_logs) == 1
        assert json.loads(log.metadata_json)["snapshots_created"] == 3
        assert filtered_logs[0].id == log.id
    finally:
        db.close()
