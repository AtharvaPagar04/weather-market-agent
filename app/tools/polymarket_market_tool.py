from datetime import UTC, datetime
from typing import Any

from app.integrations.polymarket_paper_trader_client import PolymarketPaperTraderClient
from app.models.db_models import City


class PolymarketMarketTool:
    def __init__(self, client: PolymarketPaperTraderClient) -> None:
        self.client = client

    def search_weather_market_for_city(self, city: City) -> dict:
        query = f"{city.name} rain weather tomorrow"
        result = self.client.search_markets(query)
        if not result.get("success"):
            return result

        candidate = _best_market_candidate(result.get("data"))
        if candidate is None:
            return {
                **result,
                "success": False,
                "error": "No market candidate found in pm-trader response.",
            }

        return {
            "available": result.get("available", True),
            "success": True,
            "source": result.get("source"),
            "operation": "search_weather_market_for_city",
            "data": self._candidate_to_raw_market(city=city, candidate=candidate, query=query),
            "error": None,
        }

    def fetch_price(self, market_id_or_slug: str) -> dict:
        return self.client.get_market_price(market_id_or_slug)

    def fetch_order_book(self, market_id_or_slug: str) -> dict:
        return self.client.get_order_book(market_id_or_slug)

    def _candidate_to_raw_market(self, city: City, candidate: dict[str, Any], query: str) -> dict:
        market_id = str(candidate.get("id") or candidate.get("market_id") or candidate.get("slug"))
        market_slug = str(candidate.get("slug") or candidate.get("market_slug") or market_id)
        yes_price = _first_float(
            candidate,
            ("yes_price", "price", "implied_probability", "probability", "last_price"),
        )
        no_price = _first_float(candidate, ("no_price",))
        implied_probability = _first_float(candidate, ("implied_probability", "probability"))
        best_bid = _first_float(candidate, ("best_bid", "bid"))
        best_ask = _first_float(candidate, ("best_ask", "ask"))

        return {
            "city_id": city.id,
            "market_id": market_id,
            "market_slug": market_slug,
            "question": str(candidate.get("question") or candidate.get("title") or f"Weather market for {city.name}"),
            "outcome_type": str(candidate.get("outcome_type") or "rain"),
            "yes_price": yes_price,
            "no_price": no_price,
            "implied_probability": implied_probability or yes_price,
            "volume": _first_float(candidate, ("volume", "volume_num")),
            "liquidity": _first_float(candidate, ("liquidity", "liquidity_num")),
            "end_date": candidate.get("end_date") or candidate.get("endDate"),
            "source_type": "pm_trader",
            "source_name": "polymarket-paper-trader",
            "matched_query": query,
            "order_book_available": best_bid is not None or best_ask is not None,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "midpoint": _first_float(candidate, ("midpoint", "mid_price")) or implied_probability or yes_price,
            "spread": _first_float(candidate, ("spread",)),
            "pm_trader_source": "readonly_adapter",
            "raw_payload": candidate,
            "fetched_at": datetime.now(UTC).isoformat(),
        }


def _best_market_candidate(data: Any) -> dict[str, Any] | None:
    if isinstance(data, dict):
        for key in ("markets", "results", "data"):
            value = data.get(key)
            if isinstance(value, list) and value:
                first = value[0]
                return first if isinstance(first, dict) else None
        if any(key in data for key in ("id", "market_id", "slug", "question", "title")):
            return data
    if isinstance(data, list) and data:
        first = data[0]
        return first if isinstance(first, dict) else None
    return None


def _first_float(payload: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None
