from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.prediction_service import PredictionService


router = APIRouter()


class PredictionRunRequest(BaseModel):
    city_ids: list[int] | None = None
    model_version: str = "baseline_v1"


@router.post("/predictions/run")
@router.post("/predictions/generate")
def run_predictions(request: PredictionRunRequest, db: Session = Depends(get_db)) -> dict:
    return PredictionService().run_predictions(
        db=db,
        city_ids=request.city_ids,
        model_version=request.model_version,
    )


@router.get("/predictions/latest")
def get_latest_predictions(city_id: int | None = None, db: Session = Depends(get_db)) -> list[dict]:
    predictions = PredictionService().get_latest_predictions(db=db, city_id=city_id)
    return [
        {
            "id": prediction.id,
            "city_id": prediction.city_id,
            "model_version": prediction.model_version,
            "predicted_probability": prediction.model_probability,
            "market_probability": prediction.market_probability,
            "raw_edge": prediction.raw_edge,
            "confidence_score": prediction.confidence_score,
            "prediction_label": prediction.prediction_label,
            "explanation": prediction.explanation,
            "created_at": _serialize_datetime(prediction.created_at),
        }
        for prediction in predictions
    ]


@router.get("/predictions/history/{city_id}")
def get_prediction_history(city_id: int, limit: int = 25, db: Session = Depends(get_db)) -> list[dict]:
    predictions = PredictionService().get_prediction_history(db=db, city_id=city_id, limit=limit)
    return [
        {
            "id": prediction.id,
            "city_id": prediction.city_id,
            "model_version": prediction.model_version,
            "predicted_probability": prediction.model_probability,
            "market_probability": prediction.market_probability,
            "raw_edge": prediction.raw_edge,
            "confidence_score": prediction.confidence_score,
            "prediction_label": prediction.prediction_label,
            "explanation": prediction.explanation,
            "created_at": _serialize_datetime(prediction.created_at),
        }
        for prediction in predictions
    ]


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
