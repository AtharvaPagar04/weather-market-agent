from sqlalchemy.orm import Session

from app.models.db_models import City, MarketSnapshot, Prediction, RiskReport
from app.tools.risk_calculator import RiskCalculator


class RiskService:
    def __init__(self, calculator: RiskCalculator | None = None) -> None:
        self.calculator = calculator or RiskCalculator()

    def analyze_risk(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        bankroll: float = 1000.0,
    ) -> dict:
        cities_query = db.query(City).filter(City.is_active.is_(True))
        if city_ids:
            cities_query = cities_query.filter(City.id.in_(city_ids))
        cities = cities_query.order_by(City.name.asc()).all()

        risk_reports_created = 0
        trade_allowed_count = 0
        trade_blocked_count = 0
        failed_risk_reports: list[dict[str, str | int]] = []

        for city in cities:
            prediction = self._latest_prediction_for_city(db, city.id)
            if prediction is None:
                failed_risk_reports.append({"city_id": city.id, "error_message": "Prediction is missing."})
                continue

            market_snapshot = self._market_snapshot_for_prediction(db, prediction)
            if market_snapshot is None:
                failed_risk_reports.append({"city_id": city.id, "error_message": "Market snapshot is missing."})
                continue

            analysis = self.calculator.analyze(
                prediction=prediction,
                market_snapshot=market_snapshot,
                bankroll=bankroll,
            )
            db.add(
                RiskReport(
                    city_id=city.id,
                    prediction_id=prediction.id,
                    market_snapshot_id=market_snapshot.id,
                    market_slug=market_snapshot.market_slug,
                    model_probability=analysis["model_probability"],
                    market_probability=analysis["market_probability"],
                    raw_edge=analysis["raw_edge"],
                    tradeable_edge=analysis["tradeable_edge"],
                    spread_cost=analysis["spread_cost"],
                    uncertainty_penalty=analysis["uncertainty_penalty"],
                    liquidity_penalty=analysis["liquidity_penalty"],
                    confidence=analysis["confidence"],
                    liquidity_score=analysis["liquidity_score"],
                    recommended_side=analysis["recommended_side"],
                    recommended_size=analysis["recommended_size"],
                    trade_allowed=analysis["trade_allowed"],
                    blocked_reason=analysis["blocked_reason"],
                    risk_level=analysis["risk_level"],
                    risk_decision=analysis["risk_decision"],
                    bankroll=analysis["bankroll"],
                    max_trade_risk_pct=analysis["max_trade_risk_pct"],
                    max_total_exposure_pct=analysis["max_total_exposure_pct"],
                    current_total_exposure=analysis["current_total_exposure"],
                    kelly_fraction=analysis["kelly_fraction"],
                    fractional_kelly_fraction=analysis["fractional_kelly_fraction"],
                    reason=analysis["reason"],
                )
            )
            risk_reports_created += 1
            if analysis["trade_allowed"]:
                trade_allowed_count += 1
            else:
                trade_blocked_count += 1

        db.commit()

        return {
            "success": True,
            "cities_processed": len(cities),
            "risk_reports_created": risk_reports_created,
            "trade_allowed_count": trade_allowed_count,
            "trade_blocked_count": trade_blocked_count,
            "failed_risk_reports": failed_risk_reports,
        }

    def get_latest_risk_reports(self, db: Session, city_id: int | None = None) -> list[RiskReport]:
        query = db.query(RiskReport)
        if city_id is not None:
            query = query.filter(RiskReport.city_id == city_id)
        return query.order_by(RiskReport.created_at.desc(), RiskReport.id.desc()).all()

    def _latest_prediction_for_city(self, db: Session, city_id: int) -> Prediction | None:
        return (
            db.query(Prediction)
            .filter(Prediction.city_id == city_id)
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
            .first()
        )

    def _market_snapshot_for_prediction(self, db: Session, prediction: Prediction) -> MarketSnapshot | None:
        if prediction.market_snapshot_id is not None:
            market_snapshot = (
                db.query(MarketSnapshot)
                .filter(MarketSnapshot.id == prediction.market_snapshot_id)
                .first()
            )
            if market_snapshot is not None:
                return market_snapshot

        return (
            db.query(MarketSnapshot)
            .filter(MarketSnapshot.city_id == prediction.city_id)
            .order_by(MarketSnapshot.created_at.desc(), MarketSnapshot.id.desc())
            .first()
        )
