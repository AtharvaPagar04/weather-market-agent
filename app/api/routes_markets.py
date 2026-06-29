from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.market_service import MarketService


router = APIRouter()


class MarketRefreshRequest(BaseModel):
    city_ids: list[int] | None = None
    force_mock: bool = True
    use_mock_if_unavailable: bool = True


@router.post("/markets/refresh")
def refresh_markets(request: MarketRefreshRequest, db: Session = Depends(get_db)) -> dict:
    return MarketService().refresh_markets(
        db=db,
        city_ids=request.city_ids,
        force_mock=request.force_mock,
        use_mock_if_unavailable=request.use_mock_if_unavailable,
    )


@router.get("/markets")
def get_markets(city_id: int | None = None, db: Session = Depends(get_db)) -> list[dict]:
    snapshots = MarketService().get_markets(db=db, city_id=city_id)
    return [
        {
            "id": snapshot.id,
            "city_id": snapshot.city_id,
            "market_id": snapshot.market_id,
            "market_slug": snapshot.market_slug,
            "question": snapshot.question,
            "outcome_type": snapshot.outcome_type,
            "yes_price": snapshot.yes_price,
            "no_price": snapshot.no_price,
            "implied_probability": snapshot.implied_probability,
            "volume": snapshot.volume,
            "liquidity": snapshot.liquidity,
            "source_type": snapshot.source_type,
            "source_name": snapshot.source_name,
            "matched_query": snapshot.matched_query,
            "order_book_available": snapshot.order_book_available,
            "best_bid": snapshot.best_bid,
            "best_ask": snapshot.best_ask,
            "midpoint": snapshot.midpoint,
            "spread": snapshot.spread,
            "pm_trader_source": snapshot.pm_trader_source,
            "fetched_at": _serialize_datetime(snapshot.fetched_at),
            "created_at": _serialize_datetime(snapshot.created_at),
        }
        for snapshot in snapshots
    ]


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
