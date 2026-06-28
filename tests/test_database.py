from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app import database


EXPECTED_TABLES = {
    "cities",
    "weather_snapshots",
    "market_snapshots",
    "predictions",
    "risk_reports",
    "paper_orders",
    "positions",
    "evaluation_results",
    "agent_runs",
    "agent_run_logs",
}


def test_init_db_creates_expected_tables(tmp_path, monkeypatch) -> None:
    test_db_url = f"sqlite:///{tmp_path / 'phase2.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    monkeypatch.setattr(database, "engine", test_engine)

    database.init_db()

    table_names = set(inspect(test_engine).get_table_names())
    assert EXPECTED_TABLES.issubset(table_names)


def test_database_session_can_be_opened_and_closed(tmp_path, monkeypatch) -> None:
    test_db_url = f"sqlite:///{tmp_path / 'session.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)

    database.init_db()

    db_generator = database.get_db()
    db = next(db_generator)
    assert db.is_active

    try:
        next(db_generator)
    except StopIteration:
        pass
