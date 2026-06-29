import pytest

from app.models.db_models import City, MarketSnapshot, WeatherSnapshot
from app.tools.prediction_feature_builder import PredictionFeatureBuilder


def _city() -> City:
    return City(id=1, name="Mumbai", country="India", country_code="IN", timezone="Asia/Kolkata", latitude=19.076, longitude=72.8777)


def _weather(source: str, rain_probability: float | None, confidence: float, status: str = "ok") -> WeatherSnapshot:
    return WeatherSnapshot(
        id={"global": 1, "local": 2, "apify": 3}.get(source, 4),
        city_id=1,
        source=source,
        source_confidence=confidence,
        rain_probability=rain_probability,
        status=status,
    )


def _market(probability: float = 0.46) -> MarketSnapshot:
    return MarketSnapshot(
        id=1,
        city_id=1,
        market_id="mock-mumbai-rain-tomorrow",
        market_slug="mock-mumbai-rain-tomorrow",
        question="Will it rain in Mumbai tomorrow?",
        implied_probability=probability,
        yes_price=0.5,
        source_type="mock",
    )


def test_builds_features_from_valid_weather_and_market_snapshots() -> None:
    features = PredictionFeatureBuilder().build_features(
        _city(),
        [_weather("global", 0.60, 0.80), _weather("local", 0.70, 0.85)],
        _market(),
    )

    assert features["city_id"] == 1
    assert features["city_name"] == "Mumbai"
    assert features["weather_sources_used"] == ["global", "local"]
    assert features["market_source_type"] == "mock"


def test_weighted_weather_probability_is_computed_correctly() -> None:
    features = PredictionFeatureBuilder().build_features(
        _city(),
        [_weather("global", 0.60, 0.80), _weather("local", 0.70, 0.85)],
        _market(),
    )

    expected = ((0.60 * 0.80) + (0.70 * 0.85)) / (0.80 + 0.85)
    assert features["weather_probability"] == pytest.approx(expected)


def test_market_probability_uses_implied_probability() -> None:
    features = PredictionFeatureBuilder().build_features(_city(), [_weather("global", 0.60, 0.80)], _market(0.42))

    assert features["market_probability"] == 0.42


def test_raw_edge_is_weather_minus_market_probability() -> None:
    features = PredictionFeatureBuilder().build_features(_city(), [_weather("global", 0.60, 0.80)], _market(0.42))

    assert features["raw_edge"] == pytest.approx(0.18)


def test_failed_apify_snapshot_does_not_crash_feature_building() -> None:
    features = PredictionFeatureBuilder().build_features(
        _city(),
        [_weather("global", 0.60, 0.80), _weather("apify", None, 0.0, status="failed")],
        _market(),
    )

    assert features["weather_probability"] == 0.60
    assert features["weather_sources_failed"] == ["apify"]


def test_data_quality_score_is_between_0_and_1() -> None:
    features = PredictionFeatureBuilder().build_features(
        _city(),
        [_weather("global", 0.60, 0.80), _weather("local", 0.70, 0.85), _weather("apify", 0.65, 0.75)],
        _market(),
    )

    assert 0 <= features["data_quality_score"] <= 1


def test_missing_valid_weather_raises_value_error() -> None:
    with pytest.raises(ValueError, match="weather snapshot"):
        PredictionFeatureBuilder().build_features(_city(), [_weather("apify", None, 0.0, status="failed")], _market())


def test_missing_market_snapshot_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Market snapshot"):
        PredictionFeatureBuilder().build_features(_city(), [_weather("global", 0.60, 0.80)], None)
