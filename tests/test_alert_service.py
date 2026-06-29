from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database
from app.integrations.telegram_client import TelegramClient
from app.services.agent_orchestration_service import AgentOrchestrationService
from app.services.alert_service import AlertService


def _session(tmp_path, monkeypatch):
    test_db_url = f"sqlite:///{tmp_path / 'alert_service.db'}"
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", testing_session_local)
    database.init_db()

    return testing_session_local()


def _settings(enabled: bool, token: str = "", chat_id: str = ""):
    return SimpleNamespace(
        TELEGRAM_ALERTS_ENABLED=enabled,
        TELEGRAM_BOT_TOKEN=token,
        TELEGRAM_CHAT_ID=chat_id,
    )


def test_alerts_disabled_returns_skipped_without_error(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        result = AlertService(db, settings=_settings(enabled=False)).send_test_alert()

        assert result["sent"] is False
        assert result["skipped"] is True
        assert result["reason"] == "telegram alerts disabled"
        assert "Paper trading only" in result["message"]
    finally:
        db.close()


def test_missing_token_or_chat_id_returns_skipped(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        result = AlertService(db, settings=_settings(enabled=True, token="", chat_id="123")).send_test_alert()

        assert result["sent"] is False
        assert result["skipped"] is True
        assert result["reason"] == "telegram token or chat id missing"
    finally:
        db.close()


def test_dry_run_alert_returns_formatted_message_without_network(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        client = TelegramClient(bot_token="test-token", chat_id="123")
        result = AlertService(
            db,
            settings=_settings(enabled=True, token="test-token", chat_id="123"),
            telegram_client=client,
        ).send_test_alert(dry_run=True)

        assert result["sent"] is False
        assert result["skipped"] is False
        assert result["dry_run"] is True
        assert "Weather Market Agent Demo Alert" in result["message"]
        assert "paper/simulated demo" in result["message"]
    finally:
        db.close()


def test_latest_run_alert_works_without_agent_run(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        result = AlertService(db, settings=_settings(enabled=False)).send_latest_run_alert()

        assert result["skipped"] is True
        assert "Status: no_agent_run" in result["message"]
        assert "Paper orders skipped: 0" in result["message"]
    finally:
        db.close()


def test_latest_run_alert_after_agent_pipeline_contains_paper_counts(tmp_path, monkeypatch) -> None:
    db = _session(tmp_path, monkeypatch)
    try:
        AgentOrchestrationService().run_full_pipeline(db=db)

        result = AlertService(db, settings=_settings(enabled=False)).send_latest_run_alert()
        message = result["message"]

        assert result["skipped"] is True
        assert "Status: partial" in message or "Status: completed" in message
        assert "Cities processed: 5" in message
        assert "Predictions: 5" in message
        assert "Risk reports: 5" in message
        assert "Paper trading only" in message
        assert "simulated execution" in message
        assert "wal" + "let" not in message.lower()
        assert "private" + "-key" not in message.lower()
        assert "live" + "-trading" not in message.lower()
    finally:
        db.close()
