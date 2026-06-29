from sqlalchemy.orm import Session

from app.config import get_settings
from app.integrations.telegram_client import TelegramClient
from app.models.db_models import AgentRun
from app.services.evaluation_service import EvaluationService


PAPER_ALERT_LINE = "Paper trading only - simulated execution, no real funds."
NO_OUTCOME_LINE = (
    "Accuracy metrics are not computed because realized weather outcomes are not available yet."
)


class AlertService:
    def __init__(
        self,
        db: Session,
        settings=None,
        telegram_client: TelegramClient | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.telegram_client = telegram_client or TelegramClient(
            bot_token=self.settings.TELEGRAM_BOT_TOKEN,
            chat_id=self.settings.TELEGRAM_CHAT_ID,
        )

    def get_status(self) -> dict:
        return {
            "enabled": bool(self.settings.TELEGRAM_ALERTS_ENABLED),
            "configured": self._is_configured(),
            "token_configured": bool(self.settings.TELEGRAM_BOT_TOKEN),
            "chat_id_configured": bool(self.settings.TELEGRAM_CHAT_ID),
            "source": "telegram",
            "paper_trading_only": True,
            "simulated_results": True,
        }

    def send_test_alert(self, dry_run: bool = True) -> dict:
        return self._send_message(self._format_test_message(), dry_run=dry_run)

    def send_latest_run_alert(self, dry_run: bool = True) -> dict:
        return self._send_message(self.format_latest_run_message(), dry_run=dry_run)

    def format_latest_run_message(self) -> str:
        latest_run = self._latest_agent_run()
        summary = EvaluationService(self.db).get_summary()

        status = latest_run.status if latest_run is not None else "no_agent_run"
        cities_processed = latest_run.cities_processed if latest_run is not None else 0
        predictions_created = latest_run.predictions_created if latest_run is not None else summary["predictions_count"]
        risk_reports_created = (
            latest_run.risk_reports_created if latest_run is not None else summary["risk_reports_count"]
        )
        paper_orders_created = (
            latest_run.paper_orders_created if latest_run is not None else summary["paper_orders_created"]
        )
        paper_orders_skipped = (
            latest_run.paper_orders_skipped if latest_run is not None else summary["paper_orders_skipped"]
        )

        decision_mode = (
            "WATCH / observation only"
            if summary.get("watch_decision_count", 0) > 0
            else "paper simulation summary"
        )

        return "\n".join(
            [
                "Weather Market Agent Demo Alert",
                "",
                PAPER_ALERT_LINE,
                "",
                "Latest run:",
                f"Status: {status}",
                f"Cities processed: {cities_processed}",
                f"Predictions: {predictions_created}",
                f"Risk reports: {risk_reports_created}",
                f"Paper orders created: {paper_orders_created}",
                f"Paper orders skipped: {paper_orders_skipped}",
                f"WATCH decisions: {summary.get('watch_decision_count', 0)}",
                f"Decision mode: {decision_mode}",
                "",
                NO_OUTCOME_LINE,
                "Demo outputs can be generated with POST /demo/export.",
            ]
        )

    def _send_message(self, message: str, dry_run: bool) -> dict:
        status = self.get_status()
        if not status["enabled"]:
            return {
                **status,
                "sent": False,
                "skipped": True,
                "dry_run": dry_run,
                "reason": "telegram alerts disabled",
                "message": message,
            }

        if not status["configured"]:
            return {
                **status,
                "sent": False,
                "skipped": True,
                "dry_run": dry_run,
                "reason": "telegram token or chat id missing",
                "message": message,
            }

        return {**status, **self.telegram_client.send_message(message=message, dry_run=dry_run)}

    def _format_test_message(self) -> str:
        return "\n".join(
            [
                "Weather Market Agent Demo Alert",
                "",
                PAPER_ALERT_LINE,
                "",
                "This is a safe test alert for the local paper/simulated demo.",
                NO_OUTCOME_LINE,
            ]
        )

    def _is_configured(self) -> bool:
        return bool(self.settings.TELEGRAM_BOT_TOKEN and self.settings.TELEGRAM_CHAT_ID)

    def _latest_agent_run(self) -> AgentRun | None:
        return (
            self.db.query(AgentRun)
            .order_by(AgentRun.started_at.desc(), AgentRun.id.desc())
            .first()
        )
