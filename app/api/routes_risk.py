from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.risk_service import RiskService


router = APIRouter()


class RiskAnalyzeRequest(BaseModel):
    city_ids: list[int] | None = None
    bankroll: float = 1000.0


@router.post("/risk/analyze")
def analyze_risk(request: RiskAnalyzeRequest, db: Session = Depends(get_db)) -> dict:
    return RiskService().analyze_risk(
        db=db,
        city_ids=request.city_ids,
        bankroll=request.bankroll,
    )


@router.get("/risk")
def get_risk_reports(city_id: int | None = None, db: Session = Depends(get_db)) -> list[dict]:
    reports = RiskService().get_latest_risk_reports(db=db, city_id=city_id)
    return [
        {
            "id": report.id,
            "city_id": report.city_id,
            "prediction_id": report.prediction_id,
            "market_snapshot_id": report.market_snapshot_id,
            "model_probability": report.model_probability,
            "market_probability": report.market_probability,
            "raw_edge": report.raw_edge,
            "tradeable_edge": report.tradeable_edge,
            "confidence": report.confidence,
            "risk_level": report.risk_level,
            "trade_allowed": report.trade_allowed,
            "recommended_side": report.recommended_side,
            "recommended_size": report.recommended_size,
            "risk_decision": report.risk_decision,
            "blocked_reason": report.blocked_reason,
            "reason": report.reason,
            "created_at": _serialize_datetime(report.created_at),
        }
        for report in reports
    ]


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
