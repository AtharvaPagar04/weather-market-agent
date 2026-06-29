from sqlalchemy.orm import Session

from app.models.db_models import City, MarketSnapshot
from app.tools.market_normalizer import MarketNormalizer
from app.tools.mock_market_data import MockMarketDataTool


class MarketService:
    def __init__(
        self,
        market_tool: MockMarketDataTool | None = None,
        normalizer: MarketNormalizer | None = None,
    ) -> None:
        self.market_tool = market_tool or MockMarketDataTool()
        self.normalizer = normalizer or MarketNormalizer()

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

        for city in cities:
            try:
                raw_market = self.market_tool.generate_for_city(city)
                normalized = self.normalizer.normalize(city_id=city.id, raw_market=raw_market)
            except ValueError as exc:
                failed_markets.append({"city_id": city.id, "error_message": str(exc)})
                continue

            db.add(MarketSnapshot(**normalized))
            market_snapshots_created += 1

        db.commit()

        return {
            "success": True,
            "cities_processed": len(cities),
            "market_snapshots_created": market_snapshots_created,
            "source_type": "mock",
            "fallback_used": force_mock or use_mock_if_unavailable,
            "failed_markets": failed_markets,
        }

    def get_markets(self, db: Session, city_id: int | None = None) -> list[MarketSnapshot]:
        query = db.query(MarketSnapshot)
        if city_id is not None:
            query = query.filter(MarketSnapshot.city_id == city_id)
        return query.order_by(MarketSnapshot.created_at.desc()).all()
