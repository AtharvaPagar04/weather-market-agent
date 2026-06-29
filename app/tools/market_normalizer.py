import json
from datetime import datetime
from typing import Any


class MarketNormalizer:
    def normalize(self, city_id: int, raw_market: dict[str, Any]) -> dict[str, Any]:
        market_id = _required_string(raw_market.get("market_id"), "market_id")
        question = _required_string(raw_market.get("question"), "question")

        yes_price = _clamp(_to_float(raw_market.get("yes_price")), 0, 1)
        no_price = _clamp(_to_float(raw_market.get("no_price")), 0, 1)
        if yes_price is not None and no_price is None:
            no_price = round(1 - yes_price, 10)

        implied_probability = _clamp(_to_float(raw_market.get("implied_probability")), 0, 1)
        if implied_probability is None:
            implied_probability = yes_price

        midpoint = _clamp(_to_float(raw_market.get("midpoint")), 0, 1)
        if midpoint is None:
            midpoint = implied_probability

        return {
            "city_id": city_id,
            "market_id": market_id,
            "market_slug": str(raw_market.get("market_slug") or market_id),
            "question": question,
            "outcome_type": raw_market.get("outcome_type"),
            "yes_price": yes_price,
            "no_price": no_price,
            "implied_probability": implied_probability,
            "volume": _min_value(_to_float(raw_market.get("volume")), 0),
            "liquidity": _min_value(_to_float(raw_market.get("liquidity")), 0),
            "end_date": _parse_datetime(raw_market.get("end_date")),
            "source_type": raw_market.get("source_type"),
            "source_name": raw_market.get("source_name"),
            "matched_query": raw_market.get("matched_query"),
            "order_book_available": bool(raw_market.get("order_book_available", False)),
            "best_bid": _clamp(_to_float(raw_market.get("best_bid")), 0, 1),
            "best_ask": _clamp(_to_float(raw_market.get("best_ask")), 0, 1),
            "midpoint": midpoint,
            "spread": _min_value(_to_float(raw_market.get("spread")), 0),
            "pm_trader_source": raw_market.get("pm_trader_source"),
            "raw_payload_json": json.dumps(raw_market, sort_keys=True, default=str),
            "fetched_at": _parse_datetime(raw_market.get("fetched_at")),
        }


def _required_string(value: Any, field_name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")
    return str(value)


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
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None
