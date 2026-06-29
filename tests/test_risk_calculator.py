from types import SimpleNamespace

import pytest

from app.tools.risk_calculator import RiskCalculator


def _prediction(model_probability=0.70, market_probability=0.50, confidence=0.80):
    return SimpleNamespace(
        model_probability=model_probability,
        market_probability=market_probability,
        confidence_score=confidence,
        confidence=confidence,
    )


def _market(market_probability=0.50, spread=0.01, liquidity=12000, market_slug="market"):
    return SimpleNamespace(
        implied_probability=market_probability,
        yes_price=market_probability,
        spread=spread,
        liquidity=liquidity,
        order_book_available=False,
        market_slug=market_slug,
    )


def test_calculates_raw_edge_as_model_minus_market_probability() -> None:
    result = RiskCalculator().analyze(_prediction(0.70, 0.50), _market(0.50))

    assert result["raw_edge"] == pytest.approx(0.20)


def test_calculates_tradeable_edge_minus_penalties() -> None:
    result = RiskCalculator().analyze(_prediction(0.70, 0.50, confidence=0.80), _market(0.50, spread=0.01, liquidity=12000))

    assert result["tradeable_edge"] == pytest.approx(0.19)


def test_blocks_when_confidence_is_below_minimum() -> None:
    result = RiskCalculator().analyze(_prediction(confidence=0.50), _market())

    assert result["trade_allowed"] is False
    assert result["blocked_reason"] == "confidence_below_minimum"


def test_blocks_when_abs_raw_edge_is_below_minimum() -> None:
    result = RiskCalculator().analyze(_prediction(0.53, 0.50, confidence=0.80), _market(0.50))

    assert result["trade_allowed"] is False
    assert result["blocked_reason"] == "raw_edge_below_minimum"


def test_blocks_when_tradeable_edge_is_not_positive() -> None:
    result = RiskCalculator().analyze(_prediction(0.56, 0.50, confidence=0.80), _market(0.50, spread=0.03, liquidity=1000))

    assert result["trade_allowed"] is False
    assert result["blocked_reason"] == "tradeable_edge_not_positive"


def test_blocks_when_market_slug_is_missing() -> None:
    result = RiskCalculator().analyze(_prediction(), _market(market_slug=""))

    assert result["trade_allowed"] is False
    assert result["blocked_reason"] == "market_slug_missing"


def test_allows_conservative_yes_decision_for_strong_positive_edge() -> None:
    result = RiskCalculator().analyze(_prediction(0.75, 0.50, confidence=0.85), _market(0.50, liquidity=12000))

    assert result["trade_allowed"] is True
    assert result["recommended_side"] == "YES"


def test_allows_conservative_no_decision_for_strong_negative_edge() -> None:
    result = RiskCalculator().analyze(_prediction(0.25, 0.50, confidence=0.85), _market(0.50, liquidity=12000))

    assert result["trade_allowed"] is True
    assert result["recommended_side"] == "NO"


def test_recommended_size_is_capped_at_two_percent_bankroll() -> None:
    result = RiskCalculator().analyze(_prediction(0.90, 0.40, confidence=0.90), _market(0.40, liquidity=12000), bankroll=1000)

    assert result["recommended_size"] <= 20


def test_kelly_fractions_are_clamped_between_zero_and_one() -> None:
    result = RiskCalculator().analyze(_prediction(1.0, 0.01, confidence=1.0), _market(0.01, liquidity=12000))

    assert 0 <= result["kelly_fraction"] <= 1
    assert 0 <= result["fractional_kelly_fraction"] <= 1


def test_trade_blocked_result_has_recommended_size_zero() -> None:
    result = RiskCalculator().analyze(_prediction(confidence=0.40), _market())

    assert result["trade_allowed"] is False
    assert result["recommended_size"] == 0


def test_does_not_return_execution_fields() -> None:
    result = RiskCalculator().analyze(_prediction(), _market())

    blocked_fields = {"buy", "sell", "order", "execution_command", "paper_order"}
    assert blocked_fields.isdisjoint(result)
