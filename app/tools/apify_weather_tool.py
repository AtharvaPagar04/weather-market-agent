from datetime import UTC, datetime, timedelta

from app.config import get_settings
from app.models.db_models import City


class ApifyWeatherTool:
    source = "apify"

    def __init__(self, api_token: str | None = None) -> None:
        self.api_token = api_token

    def fetch(self, city: City) -> dict:
        api_token = self.api_token
        if api_token is None:
            api_token = get_settings().APIFY_API_TOKEN

        if not api_token:
            return {
                "source": self.source,
                "status": "failed",
                "error_message": "APIFY_API_TOKEN is not configured.",
                "raw_payload": {
                    "provider": "apify",
                    "city": city.name,
                    "reason": "missing_token",
                },
            }

        city_factor = sum(ord(char) for char in city.name + city.country_code) % 9
        observed_at = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)

        return {
            "source": self.source,
            "status": "ok",
            "temperature_c": round(18.25 + city_factor + (city.latitude / 120), 2),
            "humidity_pct": 55 + city_factor,
            "rain_probability": round(0.16 + (city_factor / 95), 2),
            "wind_speed_kph": round(7.25 + (city_factor / 2), 2),
            "pressure_hpa": round(1009.0 + city_factor, 2),
            "cloud_cover_pct": 28 + city_factor,
            "precipitation_mm": round(city_factor / 22, 2),
            "condition": "apify_placeholder",
            "forecast_for": (observed_at + timedelta(hours=6)).isoformat(),
            "observed_at": observed_at.isoformat(),
            "raw_payload": {
                "provider": "apify_placeholder",
                "city": city.name,
                "network_used": False,
            },
        }
