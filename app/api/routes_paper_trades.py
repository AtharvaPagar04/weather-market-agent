from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.paper_trading_service import PaperTradingService


router = APIRouter()


class PaperTradingRunRequest(BaseModel):
    city_ids: list[int] | None = None
    dry_run: bool = False


@router.post("/paper-trades/run")
def run_paper_trading(request: PaperTradingRunRequest, db: Session = Depends(get_db)) -> dict:
    return PaperTradingService().run_paper_trading(
        db=db,
        city_ids=request.city_ids,
        dry_run=request.dry_run,
    )


@router.get("/paper-trades")
def list_paper_orders(
    city_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    orders = PaperTradingService().list_paper_orders(db=db, city_id=city_id, status=status)
    return [
        {
            "id": order.id,
            "city_id": order.city_id,
            "risk_report_id": order.risk_report_id,
            "prediction_id": order.prediction_id,
            "market_snapshot_id": order.market_snapshot_id,
            "market_id": order.market_id,
            "market_slug": order.market_slug,
            "side": order.side,
            "simulated_price": order.simulated_price,
            "size": order.size,
            "notional_value": order.notional_value,
            "model_probability": order.model_probability,
            "market_probability": order.market_probability,
            "edge": order.edge,
            "risk_level": order.risk_level,
            "status": order.status,
            "paper_execution_source": order.paper_execution_source,
            "reason": order.reason,
            "created_at": _serialize_datetime(order.created_at),
        }
        for order in orders
    ]


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
