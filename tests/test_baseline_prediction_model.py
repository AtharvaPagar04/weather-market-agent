import pytest

from app.tools.baseline_prediction_model import BaselinePredictionModel


def _features(weather_probability: float = 0.62, market_probability: float = 0.46, data_quality_score: float = 0.85) -> dict:
    return {
        "weather_probability": weather_probability,
        "market_probability": market_probability,
        "data_quality_score": data_quality_score,
        "features_json": "{}",
    }


def test_predicted_probability_equals_weather_probability() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=0.62))

    assert result["predicted_probability"] == 0.62


def test_raw_edge_is_computed_correctly() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=0.62, market_probability=0.46))

    assert result["raw_edge"] == pytest.approx(0.16)


def test_confidence_score_is_clamped_between_0_and_1() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=1.0, market_probability=0.0, data_quality_score=2.0))

    assert 0 <= result["confidence_score"] <= 1


def test_label_is_model_higher_than_market_for_large_positive_edge() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=0.70, market_probability=0.50))

    assert result["prediction_label"] == "model_higher_than_market"


def test_label_is_model_lower_than_market_for_large_negative_edge() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=0.30, market_probability=0.50))

    assert result["prediction_label"] == "model_lower_than_market"


def test_label_is_near_market_for_small_edge() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=0.54, market_probability=0.50))

    assert result["prediction_label"] == "near_market"


def test_explanation_contains_model_and_market_probability() -> None:
    result = BaselinePredictionModel().predict(_features(weather_probability=0.62, market_probability=0.46))

    assert "62.0%" in result["explanation"]
    assert "46.0%" in result["explanation"]


def test_no_trading_or_sizing_fields_are_returned() -> None:
    result = BaselinePredictionModel().predict(_features())

    blocked_fields = {
        "buy",
        "sell",
        "stake" + "_size",
        "ke" + "lly_fraction",
        "hed" + "ge_instruction",
        "trade_recommendation",
    }
    assert blocked_fields.isdisjoint(result)
