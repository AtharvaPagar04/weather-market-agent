import json
from datetime import datetime
from typing import Any

from app.models.db_models import City


SOURCE_CONFIDENCE_DEFAULTS = {
    "global": 0.80,
    "local": 0.85,
    "apify": 0.75,
    "mock": 0.50,
    "failed": 0.00,
}


def normalize_weather_payload(city: City, payload: dict[str, Any]) -> dict[str, Any]:
    source = str(payload.get("source") or "mock")
    status = str(payload.get("status") or "ok")
    error_message = payload.get("error_message")
    source_confidence = _confidence_for(source=source, status=status, payload=payload)

    return {
        "city_id": city.id,
        "source": source,
        "source_confidence": source_confidence,
        "forecast_for": _parse_datetime(payload.get("forecast_for")),
        "observed_at": _parse_datetime(payload.get("observed_at")),
        "temperature_c": _to_float(payload.get("temperature_c")),
        "humidity_pct": _clamp(_to_float(payload.get("humidity_pct")), 0, 100),
        "rain_probability": _clamp(_to_float(payload.get("rain_probability")), 0, 1),
        "wind_speed_kph": _min_value(_to_float(payload.get("wind_speed_kph")), 0),
        "pressure_hpa": _to_float(payload.get("pressure_hpa")),
        "cloud_cover_pct": _clamp(_to_float(payload.get("cloud_cover_pct")), 0, 100),
        "precipitation_mm": _min_value(_to_float(payload.get("precipitation_mm")), 0),
        "condition": payload.get("condition"),
        "raw_payload_json": json.dumps(payload.get("raw_payload", payload), sort_keys=True, default=str),
        "status": status,
        "error_message": str(error_message) if error_message else None,
    }


def _confidence_for(source: str, status: str, payload: dict[str, Any]) -> float:
    if status == "failed":
        return 0.0

    raw_confidence = payload.get("source_confidence")
    if raw_confidence is not None:
        return _clamp(_to_float(raw_confidence), 0, 1) or 0.0

    return SOURCE_CONFIDENCE_DEFAULTS.get(source, SOURCE_CONFIDENCE_DEFAULTS["mock"])


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float | None, minimum: float, maximum: float) -> float | None:
    if value is None:
        return None
    return max(minimum, min(maximum, value))


def _min_value(value: float | None, minimum: float) -> float | None:
    if value is None:
        return None
    return max(minimum, value)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, str):
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized).replace(tzinfo=None)
        except ValueError:
            return None
    return None
