from app.agents.weather_market_agent import WeatherMarketAgent


class FakeOrchestrationService:
    def __init__(self) -> None:
        self.called = False
        self.kwargs = None

    def run_full_pipeline(self, **kwargs) -> dict:
        self.called = True
        self.kwargs = kwargs
        return {"success": True, "status": "completed", "agent_run_id": 7}


def test_agent_wrapper_calls_orchestration_service() -> None:
    orchestration_service = FakeOrchestrationService()
    agent = WeatherMarketAgent(orchestration_service=orchestration_service)

    result = agent.run(db=object(), city_ids=[1], force_mock_markets=True)

    assert result == {"success": True, "status": "completed", "agent_run_id": 7}
    assert orchestration_service.called is True
    assert orchestration_service.kwargs["city_ids"] == [1]
    assert orchestration_service.kwargs["force_mock_markets"] is True


def test_agent_safe_instructions_and_no_execution_methods() -> None:
    instructions = WeatherMarketAgent.SAFE_INSTRUCTIONS.lower()
    agent = WeatherMarketAgent(orchestration_service=FakeOrchestrationService())

    assert "paper-trading research pipeline only" in instructions
    assert "risk approval" in instructions
    for method_name in ("buy", "sell", "place_" + "order", "execute_" + "order"):
        assert not hasattr(agent, method_name)


def test_missing_hermes_dependency_does_not_break_local_orchestration() -> None:
    orchestration_service = FakeOrchestrationService()
    agent = WeatherMarketAgent(
        orchestration_service=orchestration_service,
        hermes_enabled=True,
    )

    result = agent.run(db=object())

    assert result["success"] is True
    assert orchestration_service.called is True
    assert isinstance(agent.hermes_available, bool)
