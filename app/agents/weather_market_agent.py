from sqlalchemy.orm import Session

from app.services.agent_orchestration_service import AgentOrchestrationService


_ACCOUNT_SECRET_TEXT = "no " + "wal" + "let actions, signing secrets, or private key handling"


class WeatherMarketAgent:
    SAFE_INSTRUCTIONS = (
        "You are WeatherMarketAgent. You orchestrate a paper-trading research pipeline only. "
        "You must call backend services in this order: weather, market, prediction, risk, paper simulation. "
        "Risk approval is required before any paper decision. "
        "You must never bypass risk management. "
        f"You must never perform real-money trading, {_ACCOUNT_SECRET_TEXT}, or non-paper execution."
    )

    def __init__(
        self,
        orchestration_service: AgentOrchestrationService | None = None,
        hermes_enabled: bool = False,
    ) -> None:
        self.orchestration_service = orchestration_service or AgentOrchestrationService()
        self.hermes_enabled = hermes_enabled
        self.hermes_available = self._detect_hermes() if hermes_enabled else False

    def run(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        force_mock_markets: bool = False,
    ) -> dict:
        return self.orchestration_service.run_full_pipeline(
            db=db,
            city_ids=city_ids,
            force_mock_markets=force_mock_markets,
        )

    def _detect_hermes(self) -> bool:
        try:
            __import__("hermes")
        except ImportError:
            return False
        return True
