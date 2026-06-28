import json

from app.models.db_models import City
from app.tools.weather_normalizer import normalize_weather_payload


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


def test_normalizes_valid_global_payload() -> None:
    normalized = normalize_weather_payload(
        _city(),
        {
            "source": "global",
            "status": "ok",
            "temperature_c": 28.5,
            "humidity_pct": 70,
            "rain_probability": 0.4,
            "wind_speed_kph": 12,
            "pressure_hpa": 1011,
            "cloud_cover_pct": 45,
            "precipitation_mm": 0.2,
            "condition": "cloudy",
            "forecast_for": "2026-01-01T12:00:00+00:00",
            "observed_at": "2026-01-01T06:00:00+00:00",
            "raw_payload": {"provider": "test"},
        },
    )

    assert normalized["city_id"] == 1
    assert normalized["source"] == "global"
    assert normalized["source_confidence"] == 0.8
    assert normalized["temperature_c"] == 28.5
    assert normalized["condition"] == "cloudy"


def test_clamps_humidity_above_100_to_100() -> None:
    normalized = normalize_weather_payload(_city(), {"source": "global", "humidity_pct": 150})

    assert normalized["humidity_pct"] == 100


def test_clamps_rain_probability_above_1_to_1() -> None:
    normalized = normalize_weather_payload(_city(), {"source": "global", "rain_probability": 2})

    assert normalized["rain_probability"] == 1


def test_negative_wind_speed_becomes_0() -> None:
    normalized = normalize_weather_payload(_city(), {"source": "global", "wind_speed_kph": -4})

    assert normalized["wind_speed_kph"] == 0


def test_failed_payload_does_not_crash_and_confidence_is_0() -> None:
    normalized = normalize_weather_payload(
        _city(),
        {
            "source": "apify",
            "status": "failed",
            "error_message": "APIFY_API_TOKEN is not configured.",
        },
    )

    assert normalized["status"] == "failed"
    assert normalized["source_confidence"] == 0
    assert normalized["error_message"] == "APIFY_API_TOKEN is not configured."


def test_raw_payload_json_is_valid_json() -> None:
    normalized = normalize_weather_payload(
        _city(),
        {"source": "local", "raw_payload": {"nested": {"value": 1}}},
    )

    assert json.loads(normalized["raw_payload_json"]) == {"nested": {"value": 1}}
