from sqlalchemy.orm import Session

from app.models.db_models import City, WeatherSnapshot
from app.tools.apify_weather_tool import ApifyWeatherTool
from app.tools.global_weather_tool import GlobalWeatherTool
from app.tools.local_weather_tool import LocalWeatherTool
from app.tools.weather_normalizer import normalize_weather_payload


DEFAULT_WEATHER_SOURCES = ["global", "local", "apify"]


class WeatherService:
    def __init__(self, tools: dict[str, object] | None = None) -> None:
        self.tools = tools or {
            "global": GlobalWeatherTool(),
            "local": LocalWeatherTool(),
            "apify": ApifyWeatherTool(),
        }

    def refresh_weather(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        sources: list[str] | None = None,
        use_mock_on_failure: bool = True,
    ) -> dict:
        requested_sources = sources or DEFAULT_WEATHER_SOURCES
        cities_query = db.query(City).filter(City.is_active.is_(True))
        if city_ids:
            cities_query = cities_query.filter(City.id.in_(city_ids))
        cities = cities_query.order_by(City.name.asc()).all()

        snapshots_created = 0
        failed_sources: list[dict[str, str | int]] = []

        for city in cities:
            for source in requested_sources:
                tool = self.tools.get(source)
                if tool is None:
                    payload = {
                        "source": source,
                        "status": "failed",
                        "error_message": f"Weather source '{source}' is not supported.",
                        "raw_payload": {"source": source, "reason": "unsupported_source"},
                    }
                else:
                    try:
                        payload = tool.fetch(city)  # type: ignore[attr-defined]
                    except Exception as exc:
                        payload = {
                            "source": source,
                            "status": "failed",
                            "error_message": str(exc),
                            "raw_payload": {"source": source, "reason": "tool_exception"},
                        }

                normalized = normalize_weather_payload(city, payload)
                if normalized["status"] == "failed":
                    failed_sources.append(
                        {
                            "city_id": city.id,
                            "source": normalized["source"],
                            "error_message": normalized["error_message"] or "unknown error",
                        }
                    )

                db.add(WeatherSnapshot(**normalized))
                snapshots_created += 1

        db.commit()

        return {
            "success": True,
            "cities_processed": len(cities),
            "snapshots_created": snapshots_created,
            "failed_sources": failed_sources,
            "sources_used": requested_sources,
        }

    def get_latest_weather(self, db: Session, city_id: int | None = None) -> list[WeatherSnapshot]:
        query = db.query(WeatherSnapshot)
        if city_id is not None:
            query = query.filter(WeatherSnapshot.city_id == city_id)
        return query.order_by(WeatherSnapshot.created_at.desc()).all()
