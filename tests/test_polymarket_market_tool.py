from app.integrations.polymarket_paper_trader_client import PolymarketPaperTraderClient
from app.models.db_models import City
from app.tools.market_normalizer import MarketNormalizer
from app.tools.polymarket_market_tool import PolymarketMarketTool


class RecordingClient(PolymarketPaperTraderClient):
    def __init__(self, response: dict) -> None:
        super().__init__(enabled=False)
        self.response = response
        self.queries: list[str] = []

    def search_markets(self, query: str) -> dict:
        self.queries.append(query)
        return self.response

    def get_market_price(self, market_id_or_slug: str) -> dict:
        return {"success": True, "operation": "get_market_price", "data": {"market": market_id_or_slug}}

    def get_order_book(self, market_id_or_slug: str) -> dict:
        return {"success": True, "operation": "get_order_book", "data": {"market": market_id_or_slug}}


def _city() -> City:
    return City(
        id=1,
        name="Mumbai",
        country="India",
        country_code="IN",
        timezone="Asia/Kolkata",
        latitude=19.076,
        longitude=72.8777,
    )


def test_builds_weather_search_query_for_city() -> None:
    client = RecordingClient({"success": False, "error": "disabled"})
    PolymarketMarketTool(client).search_weather_market_for_city(_city())

    assert client.queries == ["Mumbai rain weather tomorrow"]


def test_unavailable_client_returns_failure_without_crash() -> None:
    result = PolymarketMarketTool(
        RecordingClient({"available": False, "success": False, "error": "disabled"})
    ).search_weather_market_for_city(_city())

    assert result["success"] is False
    assert result["error"] == "disabled"


def test_successful_search_maps_to_market_normalizer_compatible_dict() -> None:
    tool = PolymarketMarketTool(
        RecordingClient(
            {
                "available": True,
                "success": True,
                "source": "polymarket-paper-trader",
                "data": {
                    "markets": [
                        {
                            "id": "market-1",
                            "slug": "mumbai-rain-market",
                            "question": "Will it rain in Mumbai tomorrow?",
                            "yes_price": 0.64,
                            "volume": 1234,
                            "liquidity": 567,
                        }
                    ]
                },
                "error": None,
            }
        )
    )

    result = tool.search_weather_market_for_city(_city())
    raw_market = result["data"]
    normalized = MarketNormalizer().normalize(city_id=1, raw_market=raw_market)

    assert result["success"] is True
    assert normalized["source_type"] == "pm_trader"
    assert normalized["source_name"] == "polymarket-paper-trader"
    assert normalized["pm_trader_source"] == "readonly_adapter"


def test_price_and_order_book_fetch_methods_return_adapter_responses() -> None:
    tool = PolymarketMarketTool(RecordingClient({"success": False}))

    assert tool.fetch_price("market")["operation"] == "get_market_price"
    assert tool.fetch_order_book("market")["operation"] == "get_order_book"


def test_tool_does_not_expose_execution_methods() -> None:
    tool = PolymarketMarketTool(RecordingClient({"success": False}))

    assert not hasattr(tool, "buy")
    assert not hasattr(tool, "sell")
