import json
from typing import Any


SOURCE_CONFIDENCE_DEFAULTS = {
    "local": 0.85,
    "global": 0.80,
    "apify": 0.75,
    "mock": 0.50,
}


class PredictionFeatureBuilder:
    def build_features(self, city: Any, weather_snapshots: list[Any], market_snapshot: Any) -> dict:
        if market_snapshot is None:
            raise ValueError("Market snapshot is required to build prediction features.")

        valid_weather = [
            snapshot
            for snapshot in weather_snapshots
            if getattr(snapshot, "status", None) == "ok" and getattr(snapshot, "rain_probability", None) is not None
        ]
        if not valid_weather:
            raise ValueError("At least one valid weather snapshot is required to build prediction features.")

        weighted_probability_sum = 0.0
        confidence_sum = 0.0
        for snapshot in valid_weather:
            source = str(getattr(snapshot, "source", "mock"))
            source_confidence = getattr(snapshot, "source_confidence", None)
            if source_confidence is None:
                source_confidence = SOURCE_CONFIDENCE_DEFAULTS.get(source, SOURCE_CONFIDENCE_DEFAULTS["mock"])
            source_confidence = _clamp(float(source_confidence), 0, 1)
            weighted_probability_sum += _clamp(float(snapshot.rain_probability), 0, 1) * source_confidence
            confidence_sum += source_confidence

        if confidence_sum <= 0:
            raise ValueError("Weather source confidence must be greater than zero.")

        weather_probability = _clamp(weighted_probability_sum / confidence_sum, 0, 1)
        market_probability = _market_probability(market_snapshot)
        raw_edge = weather_probability - market_probability
        ok_sources = {str(getattr(snapshot, "source", "mock")) for snapshot in valid_weather}
        failed_sources = [
            str(getattr(snapshot, "source", "unknown"))
            for snapshot in weather_snapshots
            if getattr(snapshot, "status", None) != "ok"
        ]
        data_quality_score = _data_quality_score(ok_sources=ok_sources, market_snapshot=market_snapshot)

        feature_payload = {
            "city_id": city.id,
            "city_name": city.name,
            "weather_probability": weather_probability,
            "market_probability": market_probability,
            "raw_edge": raw_edge,
            "weather_sources_used": sorted(ok_sources),
            "weather_sources_failed": failed_sources,
            "market_source_type": getattr(market_snapshot, "source_type", None),
            "market_slug": getattr(market_snapshot, "market_slug", None),
            "data_quality_score": data_quality_score,
        }

        return {
            **feature_payload,
            "source_count": len(ok_sources),
            "features_json": json.dumps(feature_payload, sort_keys=True),
        }


def _market_probability(market_snapshot: Any) -> float:
    probability = getattr(market_snapshot, "implied_probability", None)
    if probability is None:
        probability = getattr(market_snapshot, "yes_price", None)
    if probability is None:
        raise ValueError("Market snapshot must include implied_probability or yes_price.")
    return _clamp(float(probability), 0, 1)


def _data_quality_score(ok_sources: set[str], market_snapshot: Any) -> float:
    score = 0.0
    if "global" in ok_sources:
        score += 0.35
    if "local" in ok_sources:
        score += 0.35
    if "apify" in ok_sources:
        score += 0.15
    if market_snapshot is not None:
        score += 0.15
    return _clamp(score, 0, 1)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
