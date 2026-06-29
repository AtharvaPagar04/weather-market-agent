from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.position_service import PositionService


router = APIRouter()


@router.get("/positions")
def list_positions(
    city_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    positions = PositionService().get_positions(db=db, city_id=city_id, status=status)
    return [
        {
            "id": position.id,
            "city_id": position.city_id,
            "market_id": position.market_id,
            "market_slug": position.market_slug,
            "side": position.side,
            "total_size": position.total_size,
            "average_price": position.average_price,
            "current_market_price": position.current_market_price,
            "total_cost": position.total_cost,
            "unrealized_pnl": position.unrealized_pnl,
            "realized_pnl": position.realized_pnl,
            "status": position.status,
            "opened_at": _serialize_datetime(position.opened_at),
            "updated_at": _serialize_datetime(position.updated_at),
        }
        for position in positions
    ]


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
