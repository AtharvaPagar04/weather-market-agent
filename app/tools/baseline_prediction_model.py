class BaselinePredictionModel:
    model_version = "baseline_v1"

    def predict(self, features: dict) -> dict:
        predicted_probability = _clamp(float(features["weather_probability"]), 0, 1)
        market_probability = _clamp(float(features["market_probability"]), 0, 1)
        raw_edge = predicted_probability - market_probability
        data_quality_score = _clamp(float(features.get("data_quality_score", 0)), 0, 1)
        confidence_score = min(1.0, data_quality_score * 0.75 + min(abs(raw_edge) * 2.0, 1.0) * 0.25)

        return {
            "model_version": self.model_version,
            "predicted_probability": predicted_probability,
            "market_probability": market_probability,
            "raw_edge": raw_edge,
            "confidence_score": confidence_score,
            "prediction_label": _prediction_label(raw_edge),
            "explanation": (
                f"Baseline model predicts {predicted_probability * 100:.1f}% rain probability "
                f"versus {market_probability * 100:.1f}% market probability."
            ),
            "features_json": features["features_json"],
        }


def _prediction_label(raw_edge: float) -> str:
    if raw_edge >= 0.10:
        return "model_higher_than_market"
    if raw_edge <= -0.10:
        return "model_lower_than_market"
    return "near_market"


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
