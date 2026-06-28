from datetime import UTC, datetime, timedelta

from app.models.db_models import City


class LocalWeatherTool:
    source = "local"

    def fetch(self, city: City) -> dict:
        city_factor = sum(ord(char) for char in city.country_code + city.name) % 10
        observed_at = datetime(2026, 1, 1, 7, 0, tzinfo=UTC)

        return {
            "source": self.source,
            "status": "ok",
            "temperature_c": round(17.5 + city_factor + (city.longitude / 180), 2),
            "humidity_pct": 57 + city_factor,
            "rain_probability": round(0.18 + (city_factor / 90), 2),
            "wind_speed_kph": round(6.5 + (city_factor / 2), 2),
            "pressure_hpa": round(1010.0 + city_factor, 2),
            "cloud_cover_pct": 30 + city_factor,
            "precipitation_mm": round(city_factor / 18, 2),
            "condition": "light_clouds" if city_factor % 2 else "clear",
            "forecast_for": (observed_at + timedelta(hours=6)).isoformat(),
            "observed_at": observed_at.isoformat(),
            "raw_payload": {
                "provider": "deterministic_local_mock",
                "city": city.name,
                "timezone": city.timezone,
            },
        }
