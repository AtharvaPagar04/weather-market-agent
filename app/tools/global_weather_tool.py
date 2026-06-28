from datetime import UTC, datetime, timedelta

from app.models.db_models import City


class GlobalWeatherTool:
    source = "global"

    def fetch(self, city: City) -> dict:
        city_factor = sum(ord(char) for char in city.name) % 12
        observed_at = datetime(2026, 1, 1, 6, 0, tzinfo=UTC)

        return {
            "source": self.source,
            "status": "ok",
            "temperature_c": round(18.0 + city_factor + (city.latitude / 90), 2),
            "humidity_pct": 52 + city_factor,
            "rain_probability": round(0.15 + (city_factor / 100), 2),
            "wind_speed_kph": round(8.0 + (city_factor / 2), 2),
            "pressure_hpa": round(1008.0 + city_factor, 2),
            "cloud_cover_pct": 25 + city_factor,
            "precipitation_mm": round(city_factor / 20, 2),
            "condition": "partly_cloudy" if city_factor % 2 else "clear",
            "forecast_for": (observed_at + timedelta(hours=6)).isoformat(),
            "observed_at": observed_at.isoformat(),
            "raw_payload": {
                "provider": "deterministic_global_mock",
                "city": city.name,
                "country_code": city.country_code,
            },
        }
