from sqlalchemy.orm import Session

from app.config import get_settings
from app.integrations.polymarket_paper_trader_client import PolymarketPaperTraderClient
from app.models.db_models import City, MarketSnapshot
from app.tools.market_normalizer import MarketNormalizer
from app.tools.mock_market_data import MockMarketDataTool
from app.tools.polymarket_market_tool import PolymarketMarketTool


class MarketService:
    def __init__(
        self,
        market_tool: MockMarketDataTool | None = None,
        normalizer: MarketNormalizer | None = None,
        polymarket_tool: PolymarketMarketTool | None = None,
    ) -> None:
        self.market_tool = market_tool or MockMarketDataTool()
        self.normalizer = normalizer or MarketNormalizer()
        self.settings = get_settings()
        self.polymarket_tool = polymarket_tool or PolymarketMarketTool(
            PolymarketPaperTraderClient(
                command=self.settings.PM_TRADER_COMMAND,
                timeout_seconds=self.settings.PM_TRADER_TIMEOUT_SECONDS,
                enabled=self.settings.PM_TRADER_ENABLED,
            )
        )

    def refresh_markets(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        force_mock: bool = True,
        use_mock_if_unavailable: bool = True,
    ) -> dict:
        cities_query = db.query(City).filter(City.is_active.is_(True))
        if city_ids:
            cities_query = cities_query.filter(City.id.in_(city_ids))
        cities = cities_query.order_by(City.name.asc()).all()

        market_snapshots_created = 0
        failed_markets: list[dict[str, str | int]] = []
        fallback_used = False
        stored_source_types: set[str] = set()
        pm_trader_available = self.polymarket_tool.client.is_available()

        for city in cities:
            raw_market: dict | None = None
            if not force_mock and self.settings.PM_TRADER_ENABLED:
                lookup_result = self.polymarket_tool.search_weather_market_for_city(city)
                if lookup_result.get("success"):
                    raw_market = lookup_result["data"]
                elif not use_mock_if_unavailable:
                    failed_markets.append(
                        {
                            "city_id": city.id,
                            "source": "pm_trader",
                            "error_message": lookup_result.get("error") or "pm-trader lookup failed",
                        }
                    )
                    continue
                else:
                    fallback_used = True
            elif not force_mock and use_mock_if_unavailable:
                fallback_used = True

            if raw_market is None:
                if force_mock or use_mock_if_unavailable:
                    raw_market = self.market_tool.generate_for_city(city)
                    fallback_used = True
                else:
                    failed_markets.append(
                        {
                            "city_id": city.id,
                            "source": "pm_trader",
                            "error_message": "PM trader integration is disabled and mock fallback is disabled.",
                        }
                    )
                    continue

            try:
                normalized = self.normalizer.normalize(city_id=city.id, raw_market=raw_market)
            except ValueError as exc:
                failed_markets.append({"city_id": city.id, "error_message": str(exc)})
                continue

            db.add(MarketSnapshot(**normalized))
            market_snapshots_created += 1
            if normalized.get("source_type"):
                stored_source_types.add(str(normalized["source_type"]))

        db.commit()

        return {
            "success": True,
            "cities_processed": len(cities),
            "market_snapshots_created": market_snapshots_created,
            "source_type": _summary_source_type(stored_source_types),
            "fallback_used": fallback_used,
            "failed_markets": failed_markets,
            "pm_trader_enabled": self.settings.PM_TRADER_ENABLED,
            "pm_trader_available": pm_trader_available,
            "readonly_mode": True,
            "order_execution_enabled": False,
        }

    def get_markets(self, db: Session, city_id: int | None = None) -> list[MarketSnapshot]:
        query = db.query(MarketSnapshot)
        if city_id is not None:
            query = query.filter(MarketSnapshot.city_id == city_id)
        return query.order_by(MarketSnapshot.created_at.desc()).all()


def _summary_source_type(source_types: set[str]) -> str:
    if len(source_types) == 1:
        return next(iter(source_types))
    if len(source_types) > 1:
        return "mixed"
    return "none"
