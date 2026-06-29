from app.tools.polymarket_paper_trade_tool import PolymarketPaperTradeTool


class FailingClient:
    def paper_buy(self, **kwargs):
        raise AssertionError("client should not be called")

    def paper_sell(self, **kwargs):
        raise AssertionError("client should not be called")


def test_disabled_paper_execution_does_not_call_client() -> None:
    result = PolymarketPaperTradeTool(client=FailingClient(), paper_execution_enabled=False).paper_buy(
        market_slug="market",
        outcome="YES",
        amount=10.0,
    )

    assert result["success"] is False
    assert result["status"] == "paper_execution_disabled"


def test_missing_market_slug_is_rejected() -> None:
    result = PolymarketPaperTradeTool().paper_buy("", "YES", 10.0)

    assert result["status"] == "paper_execution_rejected"
    assert "market_slug" in result["message"]


def test_invalid_outcome_is_rejected() -> None:
    result = PolymarketPaperTradeTool().paper_buy("market", "MAYBE", 10.0)

    assert result["status"] == "paper_execution_rejected"
    assert "YES or NO" in result["message"]


def test_non_positive_amount_is_rejected() -> None:
    result = PolymarketPaperTradeTool().paper_buy("market", "YES", 0.0)

    assert result["status"] == "paper_execution_rejected"
    assert "positive" in result["message"]


def test_paper_buy_returns_structured_response() -> None:
    result = PolymarketPaperTradeTool().paper_buy("market", "YES", 5.0)

    assert {"success", "paper_execution_source", "status", "message"}.issubset(result)


def test_paper_sell_returns_structured_response() -> None:
    result = PolymarketPaperTradeTool().paper_sell("market", "NO", 2.0)

    assert {"success", "paper_execution_source", "status", "message"}.issubset(result)


def test_no_generic_execution_methods_exist() -> None:
    tool = PolymarketPaperTradeTool()

    assert not hasattr(tool, "buy")
    assert not hasattr(tool, "sell")
    assert not hasattr(tool, "place" + "_order")
    assert not hasattr(tool, "execute" + "_order")


def test_no_credential_args_exist() -> None:
    init_vars = PolymarketPaperTradeTool.__init__.__code__.co_varnames

    assert "wal" + "let" not in init_vars
    assert "private" + "_key" not in init_vars
