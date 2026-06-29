from fastapi.testclient import TestClient

from app.integrations.polymarket_paper_trader_client import PolymarketPaperTraderClient
from app.main import app


def test_paper_trader_status_is_readonly() -> None:
    response = TestClient(app).get("/paper-trader/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["readonly_mode"] is True
    assert payload["order_execution_enabled"] is False


def test_disabled_search_returns_structured_response() -> None:
    response = TestClient(app).get("/paper-trader/search", params={"query": "Mumbai rain tomorrow"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is False
    assert payload["source"] == "polymarket-paper-trader"


def test_readonly_paper_trader_endpoints_return_200() -> None:
    client = TestClient(app)

    for path, params in (
        ("/paper-trader/price", {"market_id_or_slug": "mock-mumbai-rain-tomorrow"}),
        ("/paper-trader/book", {"market_id_or_slug": "mock-mumbai-rain-tomorrow"}),
        ("/paper-trader/portfolio", {}),
        ("/paper-trader/history", {}),
        ("/paper-trader/stats", {}),
    ):
        response = client.get(path, params=params)
        assert response.status_code == 200
        assert "success" in response.json()


def test_no_execution_routes_exist() -> None:
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    blocked_paths = {
        "/paper-trader/buy",
        "/paper-trader/sell",
        "/paper-trader/order",
        "/paper-trades/buy",
        "/paper-trades/sell",
    }

    for blocked in blocked_paths:
        assert blocked not in paths


def test_client_does_not_expose_execution_methods() -> None:
    assert not hasattr(PolymarketPaperTraderClient, "buy")
    assert not hasattr(PolymarketPaperTraderClient, "sell")
    assert not hasattr(PolymarketPaperTraderClient, "place" + "_order")
