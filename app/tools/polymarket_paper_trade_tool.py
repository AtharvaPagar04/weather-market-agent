class PolymarketPaperTradeTool:
    def __init__(self, client=None, paper_execution_enabled: bool = False) -> None:
        self.client = client
        self.paper_execution_enabled = paper_execution_enabled

    def paper_buy(self, market_slug: str, outcome: str, amount: float) -> dict:
        validation_error = _validate_inputs(market_slug=market_slug, outcome=outcome, value=amount, value_name="amount")
        if validation_error is not None:
            return validation_error
        if not self.paper_execution_enabled:
            return _disabled_response()
        if self.client is None or not hasattr(self.client, "paper_buy"):
            return _unavailable_response("pm-trader paper buy is unavailable.")
        return self.client.paper_buy(market_slug=market_slug, outcome=outcome, amount=amount)

    def paper_sell(self, market_slug: str, outcome: str, shares: float) -> dict:
        validation_error = _validate_inputs(market_slug=market_slug, outcome=outcome, value=shares, value_name="shares")
        if validation_error is not None:
            return validation_error
        if not self.paper_execution_enabled:
            return _disabled_response()
        if self.client is None or not hasattr(self.client, "paper_sell"):
            return _unavailable_response("pm-trader paper sell is unavailable.")
        return self.client.paper_sell(market_slug=market_slug, outcome=outcome, shares=shares)


def _validate_inputs(market_slug: str, outcome: str, value: float, value_name: str) -> dict | None:
    if not market_slug:
        return _validation_response("market_slug is required.")
    if outcome not in {"YES", "NO"}:
        return _validation_response("outcome must be YES or NO.")
    if value <= 0:
        return _validation_response(f"{value_name} must be positive.")
    return None


def _validation_response(message: str) -> dict:
    return {
        "success": False,
        "paper_execution_source": "local_simulation",
        "status": "paper_execution_rejected",
        "message": message,
    }


def _disabled_response() -> dict:
    return {
        "success": False,
        "paper_execution_source": "local_simulation",
        "status": "paper_execution_disabled",
        "message": "pm-trader paper execution is disabled; local audit record can still be created.",
    }


def _unavailable_response(message: str) -> dict:
    return {
        "success": False,
        "paper_execution_source": "local_simulation",
        "status": "paper_execution_unavailable",
        "message": message,
    }
