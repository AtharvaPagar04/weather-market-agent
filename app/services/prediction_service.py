import json

from sqlalchemy.orm import Session

from app.models.db_models import City, MarketSnapshot, Prediction, WeatherSnapshot
from app.tools.baseline_prediction_model import BaselinePredictionModel
from app.tools.prediction_feature_builder import PredictionFeatureBuilder


class PredictionService:
    def __init__(
        self,
        feature_builder: PredictionFeatureBuilder | None = None,
        model: BaselinePredictionModel | None = None,
    ) -> None:
        self.feature_builder = feature_builder or PredictionFeatureBuilder()
        self.model = model or BaselinePredictionModel()

    def run_predictions(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        model_version: str = "baseline_v1",
    ) -> dict:
        cities_query = db.query(City).filter(City.is_active.is_(True))
        if city_ids:
            cities_query = cities_query.filter(City.id.in_(city_ids))
        cities = cities_query.order_by(City.name.asc()).all()

        predictions_created = 0
        failed_predictions: list[dict[str, str | int]] = []

        for city in cities:
            weather_snapshots = self._latest_weather_snapshots_for_city(db, city.id)
            market_snapshot = self._latest_market_snapshot_for_city(db, city.id)
            try:
                features = self.feature_builder.build_features(city, weather_snapshots, market_snapshot)
                prediction = self.model.predict(features)
                prediction["model_version"] = model_version
            except ValueError as exc:
                failed_predictions.append({"city_id": city.id, "error_message": str(exc)})
                continue

            db.add(
                Prediction(
                    city_id=city.id,
                    market_snapshot_id=market_snapshot.id,
                    model_version=model_version,
                    prediction_type=prediction["prediction_label"],
                    model_probability=prediction["predicted_probability"],
                    market_probability=prediction["market_probability"],
                    raw_edge=prediction["raw_edge"],
                    confidence_score=prediction["confidence_score"],
                    prediction_label=prediction["prediction_label"],
                    explanation=prediction["explanation"],
                    features_json=prediction["features_json"],
                    supporting_snapshot_ids_json=json.dumps(
                        {
                            "weather_snapshot_ids": [snapshot.id for snapshot in weather_snapshots],
                            "market_snapshot_id": market_snapshot.id,
                        },
                        sort_keys=True,
                    ),
                    confidence=prediction["confidence_score"],
                    source_agreement=features["source_count"],
                    global_signal=_source_probability(weather_snapshots, "global"),
                    local_signal=_source_probability(weather_snapshots, "local"),
                    apify_signal=_source_probability(weather_snapshots, "apify"),
                    recent_trend_signal=prediction["raw_edge"],
                    source_confidence_signal=features["data_quality_score"],
                    reason=prediction["explanation"],
                    generated_by="baseline_prediction_model",
                )
            )
            predictions_created += 1

        db.commit()

        return {
            "success": True,
            "cities_processed": len(cities),
            "predictions_created": predictions_created,
            "model_version": model_version,
            "failed_predictions": failed_predictions,
        }

    def get_latest_predictions(self, db: Session, city_id: int | None = None) -> list[Prediction]:
        query = db.query(Prediction)
        if city_id is not None:
            query = query.filter(Prediction.city_id == city_id)
        return query.order_by(Prediction.created_at.desc()).all()

    def _latest_weather_snapshots_for_city(self, db: Session, city_id: int) -> list[WeatherSnapshot]:
        snapshots = (
            db.query(WeatherSnapshot)
            .filter(WeatherSnapshot.city_id == city_id)
            .order_by(WeatherSnapshot.created_at.desc(), WeatherSnapshot.id.desc())
            .all()
        )
        latest_by_source: dict[str, WeatherSnapshot] = {}
        for snapshot in snapshots:
            if snapshot.source not in latest_by_source:
                latest_by_source[snapshot.source] = snapshot
        return list(latest_by_source.values())

    def _latest_market_snapshot_for_city(self, db: Session, city_id: int) -> MarketSnapshot | None:
        return (
            db.query(MarketSnapshot)
            .filter(MarketSnapshot.city_id == city_id)
            .order_by(MarketSnapshot.created_at.desc(), MarketSnapshot.id.desc())
            .first()
        )


def _source_probability(snapshots: list[WeatherSnapshot], source: str) -> float | None:
    for snapshot in snapshots:
        if snapshot.source == source and snapshot.status == "ok":
            return snapshot.rain_probability
    return None
