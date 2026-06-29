from fastapi import APIRouter, Depends, Query

from app.config import Settings, get_settings
from app.integrations.polymarket_paper_trader_client import PolymarketPaperTraderClient


router = APIRouter()


@router.get("/paper-trader/status")
def paper_trader_status(settings: Settings = Depends(get_settings)) -> dict:
    client = _client_from_settings(settings)
    return {
        "enabled": settings.PM_TRADER_ENABLED,
        "available": client.is_available(),
        "readonly_mode": True,
        "order_execution_enabled": False,
        "source": "polymarket-paper-trader",
    }


@router.get("/paper-trader/search")
def search_paper_trader_markets(
    query: str = Query(..., min_length=1),
    settings: Settings = Depends(get_settings),
) -> dict:
    return _client_from_settings(settings).search_markets(query)


@router.get("/paper-trader/price")
def get_paper_trader_price(
    market_id_or_slug: str = Query(..., min_length=1),
    settings: Settings = Depends(get_settings),
) -> dict:
    return _client_from_settings(settings).get_market_price(market_id_or_slug)


@router.get("/paper-trader/book")
def get_paper_trader_book(
    market_id_or_slug: str = Query(..., min_length=1),
    settings: Settings = Depends(get_settings),
) -> dict:
    return _client_from_settings(settings).get_order_book(market_id_or_slug)


@router.get("/paper-trader/portfolio")
def get_paper_trader_portfolio(settings: Settings = Depends(get_settings)) -> dict:
    return _client_from_settings(settings).get_portfolio()


@router.get("/paper-trader/history")
def get_paper_trader_history(settings: Settings = Depends(get_settings)) -> dict:
    return _client_from_settings(settings).get_history()


@router.get("/paper-trader/stats")
def get_paper_trader_stats(settings: Settings = Depends(get_settings)) -> dict:
    return _client_from_settings(settings).get_stats()


def _client_from_settings(settings: Settings) -> PolymarketPaperTraderClient:
    return PolymarketPaperTraderClient(
        command=settings.PM_TRADER_COMMAND,
        timeout_seconds=settings.PM_TRADER_TIMEOUT_SECONDS,
        enabled=settings.PM_TRADER_ENABLED,
    )
