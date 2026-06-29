import csv
import json
import os

from sqlalchemy.orm import Session

from app.models.db_models import AgentRun, PaperOrder, Prediction, RiskReport
from app.services.agent_log_service import AgentLogService
from app.services.market_service import MarketService
from app.services.paper_trading_service import PaperTradingService
from app.services.position_service import PositionService
from app.services.prediction_service import PredictionService
from app.services.risk_service import RiskService
from app.services.weather_service import WeatherService


NO_OUTCOME_MESSAGE = (
    "Realized weather outcomes are not available yet, so accuracy, Brier score, and log loss are not computed."
)


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.prediction_service = PredictionService()
        self.risk_service = RiskService()
        self.paper_trading_service = PaperTradingService()
        self.position_service = PositionService()
        self.market_service = MarketService()
        self.weather_service = WeatherService()
        self.agent_log_service = AgentLogService()

    def get_summary(self) -> dict:
        predictions = self.prediction_service.get_latest_predictions(self.db)
        risk_reports = self.risk_service.get_latest_risk_reports(self.db)
        paper_orders = self.paper_trading_service.list_paper_orders(self.db)
        positions = self.position_service.get_positions(self.db)
        markets = self.market_service.get_markets(self.db)
        weather = self.weather_service.get_latest_weather(self.db)
        agent_runs = self.agent_log_service.list_runs(self.db)

        predictions_count = len(predictions)
        cities_evaluated = len(set(p.city_id for p in predictions))

        avg_model_prob = _average(_safe_float(p.model_probability) for p in predictions)
        avg_market_prob = _average(_safe_float(p.market_probability) for p in predictions)
        avg_raw_edge = _average(_safe_float(p.raw_edge) for p in predictions)
        avg_confidence = _average(_safe_float(p.confidence_score) for p in predictions)

        risk_reports_count = len(risk_reports)
        trade_allowed_count = sum(1 for r in risk_reports if r.trade_allowed)
        trade_blocked_count = sum(1 for r in risk_reports if not r.trade_allowed)
        watch_decision_count = sum(1 for r in risk_reports if r.risk_decision == "WATCH")

        paper_orders_created = sum(1 for o in paper_orders if o.status == "paper_order_created")
        paper_orders_skipped = sum(1 for o in paper_orders if o.status == "paper_order_skipped")

        simulated_positions_count = sum(1 for p in positions if p.status == "open")
        simulated_total_cost = sum(_safe_float(p.total_cost) for p in positions if p.status == "open")
        simulated_unrealized_pnl = sum(_safe_float(p.unrealized_pnl) for p in positions if p.status == "open")

        market_snapshots_count = len(markets)
        mock_market_count = sum(1 for m in markets if _market_source_type(m) == "mock")
        fallback_market_count = sum(1 for m in markets if _is_market_fallback(m))

        weather_snapshots_count = len(weather)

        agent_runs_count = len(agent_runs)
        latest_agent_status = agent_runs[0].status if agent_runs else "unknown"
        latest_agent_summary = _parse_json_like(agent_runs[0].summary_json, []) if agent_runs else []
        apify_missing_token_count = _apify_missing_token_count(weather)

        summary = {
            "predictions_count": predictions_count,
            "cities_evaluated": cities_evaluated,
            "average_model_probability": avg_model_prob,
            "average_market_probability": avg_market_prob,
            "average_raw_edge": avg_raw_edge,
            "average_confidence": avg_confidence,
            "risk_reports_count": risk_reports_count,
            "paper_orders_created": paper_orders_created,
            "paper_orders_skipped": paper_orders_skipped,
            "trade_allowed_count": trade_allowed_count,
            "trade_blocked_count": trade_blocked_count,
            "watch_decision_count": watch_decision_count,
            "simulated_positions_count": simulated_positions_count,
            "simulated_total_cost": simulated_total_cost,
            "simulated_unrealized_pnl": simulated_unrealized_pnl,
            "market_snapshots_count": market_snapshots_count,
            "weather_snapshots_count": weather_snapshots_count,
            "mock_market_count": mock_market_count,
            "fallback_market_count": fallback_market_count,
            "apify_missing_token_count": apify_missing_token_count,
            "agent_runs_count": agent_runs_count,
            "latest_agent_status": latest_agent_status,
            "latest_agent_summary_count": len(latest_agent_summary) if isinstance(latest_agent_summary, list) else 0,
            "outcome_data_available": False,
            "accuracy_metrics_available": False,
            "message": NO_OUTCOME_MESSAGE,
        }

        return summary

    def run_evaluation(self) -> dict:
        return self.get_summary()

    def export_demo_output(self, output_dir: str = "demo_output") -> dict:
        os.makedirs(output_dir, exist_ok=True)

        summary = self.get_summary()

        summary_path = os.path.join(output_dir, "results_summary.csv")
        with open(summary_path, mode="w", newline="") as f:
            summary_with_labels = {
                "paper_trading_only": True,
                "simulated_results": True,
                "demo_results": True,
                **summary
            }
            writer = csv.DictWriter(f, fieldnames=summary_with_labels.keys())
            writer.writeheader()
            writer.writerow(summary_with_labels)

        preds_path = os.path.join(output_dir, "sample_predictions.json")
        preds_data = [_prediction_export_row(p) for p in self.prediction_service.get_latest_predictions(self.db)]
        with open(preds_path, "w") as f:
            json.dump(preds_data, f, indent=2)

        orders_path = os.path.join(output_dir, "sample_orders.json")
        orders_data = self._paper_decision_export_rows()
        with open(orders_path, "w") as f:
            json.dump(orders_data, f, indent=2)

        pm_path = os.path.join(output_dir, "pm_trader_stats.json")
        pm_data = {
            "pm_trader_available": False,
            "readonly_mode": True,
            "order_execution_enabled": False,
            "source": "mock_or_unavailable",
            "paper_trading_only": True,
            "simulated_results": True,
            "demo_results": True,
            "message": "Polymarket paper-trader integration is read-only/mock fallback in this demo environment."
        }
        with open(pm_path, "w") as f:
            json.dump(pm_data, f, indent=2)

        return {
            "status": "success",
            "files_created": [
                summary_path,
                preds_path,
                orders_path,
                pm_path
            ]
        }

    def _paper_decision_export_rows(self) -> list[dict]:
        orders = self.paper_trading_service.list_paper_orders(self.db)
        if orders:
            return [self._paper_order_export_row(order) for order in orders]

        agent_rows = self._latest_agent_summary_export_rows()
        if agent_rows:
            return agent_rows

        risk_reports = self.risk_service.get_latest_risk_reports(self.db)
        return [_risk_report_export_row(report) for report in risk_reports]

    def _latest_agent_summary_export_rows(self) -> list[dict]:
        latest_run = self.db.query(AgentRun).order_by(AgentRun.started_at.desc(), AgentRun.id.desc()).first()
        if latest_run is None:
            return []

        summary = _parse_json_like(latest_run.summary_json, [])
        if not isinstance(summary, list):
            return []

        rows = []
        for item in summary:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "city_id": item.get("city_id"),
                    "city_name": item.get("city_name"),
                    "risk_decision": item.get("risk_decision"),
                    "trade_allowed": item.get("paper_status") == "paper_order_created",
                    "recommended_size": 0.0,
                    "paper_status": item.get("paper_status") or "paper_decision_recorded",
                    "model_probability": _safe_float(item.get("model_probability")),
                    "market_probability": _safe_float(item.get("market_probability")),
                    "edge": _safe_float(item.get("raw_edge")),
                    "paper_trading_only": True,
                    "simulated_results": True,
                    "demo_results": True,
                    "message": "Demo paper decision reconstructed from the latest agent run summary.",
                }
            )
        return rows

    def _paper_order_export_row(self, order: PaperOrder) -> dict:
        risk_report = None
        if order.risk_report_id is not None:
            risk_report = self.db.query(RiskReport).filter(RiskReport.id == order.risk_report_id).first()

        return {
            "city_id": order.city_id,
            "risk_report_id": order.risk_report_id,
            "prediction_id": order.prediction_id,
            "market_snapshot_id": order.market_snapshot_id,
            "market_slug": order.market_slug,
            "risk_decision": getattr(risk_report, "risk_decision", None) or order.risk_level,
            "trade_allowed": order.status == "paper_order_created",
            "recommended_size": _safe_float(order.size) if order.status == "paper_order_created" else 0.0,
            "notional_value": _safe_float(order.notional_value),
            "paper_status": order.status,
            "paper_execution_source": order.paper_execution_source,
            "model_probability": _safe_float(order.model_probability),
            "market_probability": _safe_float(order.market_probability),
            "edge": _safe_float(order.edge),
            "paper_trading_only": True,
            "simulated_results": True,
            "demo_results": True,
            "message": "Simulated paper order decision.",
            "created_at": _isoformat_or_none(order.created_at),
        }


def _prediction_export_row(prediction: Prediction) -> dict:
    return {
        "city_id": prediction.city_id,
        "market_snapshot_id": prediction.market_snapshot_id,
        "market_probability": _safe_float(prediction.market_probability),
        "model_probability": _safe_float(prediction.model_probability),
        "confidence": _safe_float(prediction.confidence_score),
        "edge": _safe_float(prediction.raw_edge),
        "prediction_label": prediction.prediction_label,
        "model_version": prediction.model_version,
        "paper_trading_only": True,
        "simulated_results": True,
        "demo_results": True,
        "created_at": _isoformat_or_none(prediction.created_at),
    }


def _risk_report_export_row(report: RiskReport) -> dict:
    return {
        "city_id": report.city_id,
        "risk_report_id": report.id,
        "prediction_id": report.prediction_id,
        "market_snapshot_id": report.market_snapshot_id,
        "market_slug": report.market_slug,
        "risk_decision": report.risk_decision,
        "trade_allowed": bool(report.trade_allowed),
        "recommended_size": _safe_float(report.recommended_size) if report.trade_allowed else 0.0,
        "paper_status": "paper_order_pending" if report.trade_allowed else "paper_order_skipped",
        "paper_execution_source": "local_simulation",
        "model_probability": _safe_float(report.model_probability),
        "market_probability": _safe_float(report.market_probability),
        "edge": _safe_float(report.raw_edge),
        "paper_trading_only": True,
        "simulated_results": True,
        "demo_results": True,
        "message": "Demo paper decision reconstructed from risk analysis.",
        "created_at": _isoformat_or_none(report.created_at),
    }


def _safe_float(value) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _average(values) -> float:
    safe_values = [value for value in values if value is not None]
    return sum(safe_values) / len(safe_values) if safe_values else 0.0


def _market_source_type(market) -> str:
    return str(getattr(market, "source_type", "") or "").lower()


def _is_market_fallback(market) -> bool:
    source_type = _market_source_type(market)
    pm_source = str(getattr(market, "pm_trader_source", "") or "").lower()
    return source_type in {"mock", "fallback"} or "fallback" in pm_source


def _apify_missing_token_count(weather_snapshots) -> int:
    count = 0
    for snapshot in weather_snapshots:
        if str(getattr(snapshot, "source", "")).lower() != "apify":
            continue
        text = f"{getattr(snapshot, 'status', '')} {getattr(snapshot, 'error_message', '')}".lower()
        if "failed" in text and ("token" in text or "configured" in text):
            count += 1
    return count


def _parse_json_like(value, default):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _isoformat_or_none(value) -> str | None:
    return value.isoformat() if value else None
