import json

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.db_models import City, MarketSnapshot, PaperOrder, Prediction, RiskReport
from app.services.position_service import PositionService
from app.tools.polymarket_paper_trade_tool import PolymarketPaperTradeTool


class PaperTradingService:
    def __init__(
        self,
        paper_trade_tool: PolymarketPaperTradeTool | None = None,
        position_service: PositionService | None = None,
    ) -> None:
        self.settings = get_settings()
        self.paper_trade_tool = paper_trade_tool or PolymarketPaperTradeTool(
            paper_execution_enabled=self.settings.PM_TRADER_PAPER_EXECUTION_ENABLED
        )
        self.position_service = position_service or PositionService()

    def run_paper_trading(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        dry_run: bool = False,
    ) -> dict:
        cities_query = db.query(City).filter(City.is_active.is_(True))
        if city_ids:
            cities_query = cities_query.filter(City.id.in_(city_ids))
        cities = cities_query.order_by(City.name.asc()).all()

        paper_orders_created = 0
        paper_orders_skipped = 0
        positions_updated = 0
        failed_paper_orders: list[dict[str, str | int]] = []

        for city in cities:
            risk_report = self._latest_risk_report_for_city(db, city.id)
            if risk_report is None:
                failed_paper_orders.append({"city_id": city.id, "error_message": "Risk report is missing."})
                continue

            if self._existing_order_for_risk_report(db, risk_report.id) is not None:
                paper_orders_skipped += 1
                continue

            prediction = self._prediction_for_risk_report(db, risk_report)
            market_snapshot = self._market_snapshot_for_risk_report(db, risk_report)
            if prediction is None or market_snapshot is None:
                failed_paper_orders.append({"city_id": city.id, "error_message": "Prediction or market snapshot is missing."})
                continue

            order_data = self._build_order_data(
                city_id=city.id,
                risk_report=risk_report,
                prediction=prediction,
                market_snapshot=market_snapshot,
            )
            if dry_run:
                if order_data["status"] == "paper_order_created":
                    paper_orders_created += 1
                else:
                    paper_orders_skipped += 1
                continue

            paper_order = PaperOrder(**order_data)
            db.add(paper_order)
            db.flush()
            if paper_order.status == "paper_order_created":
                paper_orders_created += 1
                update_result = self.position_service.update_position_from_order(db, paper_order)
                if update_result["position_updated"]:
                    positions_updated += 1
            else:
                paper_orders_skipped += 1

        if not dry_run:
            db.commit()

        return {
            "success": True,
            "cities_processed": len(cities),
            "paper_orders_created": paper_orders_created,
            "paper_orders_skipped": paper_orders_skipped,
            "positions_updated": positions_updated,
            "failed_paper_orders": failed_paper_orders,
        }

    def list_paper_orders(
        self,
        db: Session,
        city_id: int | None = None,
        status: str | None = None,
    ) -> list[PaperOrder]:
        query = db.query(PaperOrder)
        if city_id is not None:
            query = query.filter(PaperOrder.city_id == city_id)
        if status is not None:
            query = query.filter(PaperOrder.status == status)
        return query.order_by(PaperOrder.created_at.desc(), PaperOrder.id.desc()).all()

    def _build_order_data(
        self,
        city_id: int,
        risk_report: RiskReport,
        prediction: Prediction,
        market_snapshot: MarketSnapshot,
    ) -> dict:
        if not risk_report.trade_allowed:
            return self._skipped_order(
                city_id=city_id,
                risk_report=risk_report,
                prediction=prediction,
                market_snapshot=market_snapshot,
                reason=risk_report.blocked_reason or "risk_report_not_approved",
            )

        if risk_report.recommended_side not in {"YES", "NO"}:
            return self._skipped_order(city_id, risk_report, prediction, market_snapshot, "recommended_side_invalid")
        if (risk_report.recommended_size or 0.0) <= 0:
            return self._skipped_order(city_id, risk_report, prediction, market_snapshot, "recommended_size_not_positive")
        if not risk_report.market_slug:
            return self._skipped_order(city_id, risk_report, prediction, market_snapshot, "market_slug_missing")

        simulated_price = market_snapshot.yes_price if risk_report.recommended_side == "YES" else market_snapshot.no_price
        if simulated_price is None:
            simulated_price = market_snapshot.implied_probability
        pm_trader_result = self.paper_trade_tool.paper_buy(
            market_slug=risk_report.market_slug,
            outcome=risk_report.recommended_side,
            amount=risk_report.recommended_size,
        )
        return {
            "city_id": city_id,
            "risk_report_id": risk_report.id,
            "prediction_id": prediction.id,
            "market_snapshot_id": market_snapshot.id,
            "market_id": market_snapshot.market_id,
            "market_slug": risk_report.market_slug,
            "side": risk_report.recommended_side,
            "outcome": risk_report.recommended_side,
            "requested_amount": risk_report.recommended_size,
            "size": risk_report.recommended_size,
            "notional_value": risk_report.recommended_size,
            "simulated_price": simulated_price,
            "model_probability": risk_report.model_probability,
            "market_probability": risk_report.market_probability,
            "edge": risk_report.raw_edge,
            "risk_level": risk_report.risk_level,
            "status": "paper_order_created",
            "paper_execution_source": self.settings.PAPER_TRADING_EXECUTION_SOURCE,
            "pm_trader_result_json": json.dumps(pm_trader_result, sort_keys=True),
            "audit_sync_status": "local_only",
            "reason": risk_report.reason,
        }

    def _skipped_order(
        self,
        city_id: int,
        risk_report: RiskReport,
        prediction: Prediction,
        market_snapshot: MarketSnapshot,
        reason: str,
    ) -> dict:
        return {
            "city_id": city_id,
            "risk_report_id": risk_report.id,
            "prediction_id": prediction.id,
            "market_snapshot_id": market_snapshot.id,
            "market_id": market_snapshot.market_id,
            "market_slug": risk_report.market_slug,
            "side": "NONE",
            "outcome": "NONE",
            "requested_amount": 0.0,
            "size": 0.0,
            "notional_value": 0.0,
            "simulated_price": 0.0,
            "model_probability": risk_report.model_probability,
            "market_probability": risk_report.market_probability,
            "edge": risk_report.raw_edge,
            "risk_level": risk_report.risk_level,
            "status": "paper_order_skipped",
            "paper_execution_source": self.settings.PAPER_TRADING_EXECUTION_SOURCE,
            "audit_sync_status": "local_only",
            "reason": reason,
        }

    def _latest_risk_report_for_city(self, db: Session, city_id: int) -> RiskReport | None:
        return (
            db.query(RiskReport)
            .filter(RiskReport.city_id == city_id)
            .order_by(RiskReport.created_at.desc(), RiskReport.id.desc())
            .first()
        )

    def _existing_order_for_risk_report(self, db: Session, risk_report_id: int) -> PaperOrder | None:
        return db.query(PaperOrder).filter(PaperOrder.risk_report_id == risk_report_id).first()

    def _prediction_for_risk_report(self, db: Session, risk_report: RiskReport) -> Prediction | None:
        return db.query(Prediction).filter(Prediction.id == risk_report.prediction_id).first()

    def _market_snapshot_for_risk_report(self, db: Session, risk_report: RiskReport) -> MarketSnapshot | None:
        if risk_report.market_snapshot_id is None:
            return None
        return db.query(MarketSnapshot).filter(MarketSnapshot.id == risk_report.market_snapshot_id).first()
