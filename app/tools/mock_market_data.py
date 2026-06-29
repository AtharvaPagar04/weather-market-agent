from datetime import UTC, datetime, timedelta
import re

from app.models.db_models import City


CITY_MOCK_YES_PRICE = {
    "Mumbai": 0.62,
    "London": 0.58,
    "New York": 0.46,
    "Tokyo": 0.41,
    "Sydney": 0.37,
}


class MockMarketDataTool:
    def generate_for_city(self, city: City) -> dict:
        yes_price = CITY_MOCK_YES_PRICE.get(city.name, 0.50)
        market_slug = f"mock-{_slugify(city.name)}-rain-tomorrow"
        fetched_at = datetime(2026, 1, 1, 9, 0, tzinfo=UTC)
        city_factor = sum(ord(char) for char in city.name) % 20

        return {
            "city_id": city.id,
            "market_id": market_slug,
            "market_slug": market_slug,
            "question": f"Will it rain in {city.name} tomorrow?",
            "outcome_type": "rain",
            "yes_price": yes_price,
            "no_price": round(1 - yes_price, 2),
            "implied_probability": yes_price,
            "volume": float(1000 + (city_factor * 125)),
            "liquidity": float(500 + (city_factor * 75)),
            "end_date": (fetched_at + timedelta(days=1)).isoformat(),
            "source_type": "mock",
            "source_name": "mock_market_generator",
            "matched_query": f"{city.name} rain",
            "order_book_available": False,
            "best_bid": None,
            "best_ask": None,
            "midpoint": yes_price,
            "spread": 0.00,
            "pm_trader_source": "mock_fallback",
            "raw_payload": {
                "provider": "mock_market_generator",
                "mode": "fallback_demo_only",
                "city": city.name,
                "country_code": city.country_code,
            },
            "fetched_at": fetched_at.isoformat(),
        }


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown-city"
