import json

import pytest

from app.tools.market_normalizer import MarketNormalizer


def _raw_market() -> dict:
    return {
        "market_id": "mock-mumbai-rain-tomorrow",
        "market_slug": "mock-mumbai-rain-tomorrow",
        "question": "Will it rain in Mumbai tomorrow?",
        "outcome_type": "rain",
        "yes_price": 0.62,
        "no_price": 0.38,
        "implied_probability": 0.62,
        "volume": 1000,
        "liquidity": 500,
        "source_type": "mock",
        "source_name": "mock_market_generator",
        "matched_query": "Mumbai rain",
        "order_book_available": False,
        "midpoint": 0.62,
        "spread": 0,
        "pm_trader_source": "mock_fallback",
        "raw_payload": {"provider": "test"},
        "fetched_at": "2026-01-01T09:00:00+00:00",
    }


def test_normalizes_valid_mock_market() -> None:
    normalized = MarketNormalizer().normalize(city_id=1, raw_market=_raw_market())

    assert normalized["city_id"] == 1
    assert normalized["market_id"] == "mock-mumbai-rain-tomorrow"
    assert normalized["question"] == "Will it rain in Mumbai tomorrow?"
    assert normalized["source_type"] == "mock"
    assert normalized["yes_price"] == 0.62
    assert normalized["no_price"] == 0.38


def test_sets_no_price_from_yes_price_if_missing() -> None:
    raw_market = _raw_market()
    raw_market.pop("no_price")

    normalized = MarketNormalizer().normalize(city_id=1, raw_market=raw_market)

    assert normalized["no_price"] == 0.38


def test_sets_implied_probability_from_yes_price_if_missing() -> None:
    raw_market = _raw_market()
    raw_market.pop("implied_probability")

    normalized = MarketNormalizer().normalize(city_id=1, raw_market=raw_market)

    assert normalized["implied_probability"] == 0.62


def test_clamps_invalid_high_and_low_prices() -> None:
    raw_market = _raw_market()
    raw_market["yes_price"] = 2
    raw_market["no_price"] = -1
    raw_market["implied_probability"] = 5

    normalized = MarketNormalizer().normalize(city_id=1, raw_market=raw_market)

    assert normalized["yes_price"] == 1
    assert normalized["no_price"] == 0
    assert normalized["implied_probability"] == 1


def test_negative_volume_and_liquidity_become_0() -> None:
    raw_market = _raw_market()
    raw_market["volume"] = -10
    raw_market["liquidity"] = -20

    normalized = MarketNormalizer().normalize(city_id=1, raw_market=raw_market)

    assert normalized["volume"] == 0
    assert normalized["liquidity"] == 0


def test_empty_question_raises_value_error() -> None:
    raw_market = _raw_market()
    raw_market["question"] = ""

    with pytest.raises(ValueError, match="question"):
        MarketNormalizer().normalize(city_id=1, raw_market=raw_market)


def test_empty_market_id_raises_value_error() -> None:
    raw_market = _raw_market()
    raw_market["market_id"] = ""

    with pytest.raises(ValueError, match="market_id"):
        MarketNormalizer().normalize(city_id=1, raw_market=raw_market)


def test_raw_payload_json_is_valid_json() -> None:
    normalized = MarketNormalizer().normalize(city_id=1, raw_market=_raw_market())

    assert json.loads(normalized["raw_payload_json"])["market_id"] == "mock-mumbai-rain-tomorrow"
