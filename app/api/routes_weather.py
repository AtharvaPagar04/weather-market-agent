from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.weather_service import DEFAULT_WEATHER_SOURCES, WeatherService


router = APIRouter()


class WeatherRefreshRequest(BaseModel):
    city_ids: list[int] | None = None
    sources: list[str] | None = Field(default_factory=lambda: DEFAULT_WEATHER_SOURCES.copy())
    use_mock_on_failure: bool = True


@router.post("/weather/refresh")
def refresh_weather(request: WeatherRefreshRequest, db: Session = Depends(get_db)) -> dict:
    return WeatherService().refresh_weather(
        db=db,
        city_ids=request.city_ids,
        sources=request.sources,
        use_mock_on_failure=request.use_mock_on_failure,
    )


@router.get("/weather/latest")
def latest_weather(city_id: int | None = None, db: Session = Depends(get_db)) -> list[dict]:
    snapshots = WeatherService().get_latest_weather(db=db, city_id=city_id)
    return [
        {
            "id": snapshot.id,
            "city_id": snapshot.city_id,
            "source": snapshot.source,
            "status": snapshot.status,
            "rain_probability": snapshot.rain_probability,
            "temperature_c": snapshot.temperature_c,
            "humidity_pct": snapshot.humidity_pct,
            "created_at": _serialize_datetime(snapshot.created_at),
            "error_message": snapshot.error_message,
        }
        for snapshot in snapshots
    ]


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
