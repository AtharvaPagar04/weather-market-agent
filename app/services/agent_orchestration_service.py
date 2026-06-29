from sqlalchemy.orm import Session

from app.models.db_models import City, PaperOrder, Prediction, RiskReport
from app.services.agent_log_service import AgentLogService
from app.services.city_service import CityService
from app.services.market_service import MarketService
from app.services.paper_trading_service import PaperTradingService
from app.services.prediction_service import PredictionService
from app.services.risk_service import RiskService
from app.services.weather_service import WeatherService


class AgentOrchestrationService:
    def __init__(
        self,
        log_service: AgentLogService | None = None,
        weather_service: WeatherService | None = None,
        market_service: MarketService | None = None,
        prediction_service: PredictionService | None = None,
        risk_service: RiskService | None = None,
        paper_trading_service: PaperTradingService | None = None,
    ) -> None:
        self.log_service = log_service or AgentLogService()
        self.weather_service = weather_service or WeatherService()
        self.market_service = market_service or MarketService()
        self.prediction_service = prediction_service or PredictionService()
        self.risk_service = risk_service or RiskService()
        self.paper_trading_service = paper_trading_service or PaperTradingService()

    def run_full_pipeline(
        self,
        db: Session,
        city_ids: list[int] | None = None,
        force_mock_markets: bool = False,
        run_evaluation_after: bool = False,
    ) -> dict:
        agent_run = self.log_service.create_run(
            db=db,
            run_type="full_pipeline",
            cities_requested=len(city_ids) if city_ids is not None else 0,
        )
        counts = _empty_counts()
        failures: list[dict] = []

        try:
            active_cities = CityService.get_active_cities(db)
            if not active_cities:
                seed_result = CityService.seed_default_cities(db)
                self.log_service.add_log(
                    db=db,
                    agent_run_id=agent_run.id,
                    step_name="cities",
                    status="success",
                    message="Default cities seeded.",
                    metadata=seed_result,
                )
                active_cities = CityService.get_active_cities(db)
            else:
                self.log_service.add_log(
                    db=db,
                    agent_run_id=agent_run.id,
                    step_name="cities",
                    status="success",
                    message="Active cities loaded.",
                    metadata={"total_active_cities": len(active_cities)},
                )

            selected_cities = _select_cities(active_cities, city_ids)
            selected_city_ids = [city.id for city in selected_cities]
            counts["cities_requested"] = len(city_ids) if city_ids is not None else len(selected_city_ids)
            counts["cities_processed"] = len(selected_city_ids)

            if not selected_city_ids:
                return self._finish_failed_run(
                    db=db,
                    agent_run=agent_run,
                    counts=counts,
                    message="Agent run failed: no active cities matched the request.",
                )

            self._update_running_counts(db, agent_run, counts)

            weather_result = self.weather_service.refresh_weather(db=db, city_ids=selected_city_ids)
            counts["weather_snapshots_created"] = weather_result["snapshots_created"]
            failures.extend(_failure_items(weather_result, "failed_sources"))
            self._log_step_result(
                db,
                agent_run.id,
                "weather",
                "Weather refresh completed.",
                weather_result,
                "failed_sources",
            )

            market_result = self.market_service.refresh_markets(
                db=db,
                city_ids=selected_city_ids,
                force_mock=force_mock_markets,
                use_mock_if_unavailable=True,
            )
            counts["market_snapshots_created"] = market_result["market_snapshots_created"]
            failures.extend(_failure_items(market_result, "failed_markets"))
            self._log_step_result(
                db,
                agent_run.id,
                "markets",
                "Market refresh completed.",
                market_result,
                "failed_markets",
                fallback_used=bool(market_result.get("fallback_used")),
            )

            prediction_result = self.prediction_service.run_predictions(db=db, city_ids=selected_city_ids)
            counts["predictions_created"] = prediction_result["predictions_created"]
            failures.extend(_failure_items(prediction_result, "failed_predictions"))
            self._log_step_result(
                db,
                agent_run.id,
                "predictions",
                "Prediction generation completed.",
                prediction_result,
                "failed_predictions",
            )

            risk_result = self.risk_service.analyze_risk(db=db, city_ids=selected_city_ids)
            counts["risk_reports_created"] = risk_result["risk_reports_created"]
            failures.extend(_failure_items(risk_result, "failed_risk_reports"))
            self._log_step_result(
                db,
                agent_run.id,
                "risk",
                "Risk analysis completed.",
                risk_result,
                "failed_risk_reports",
            )

            paper_result = self.paper_trading_service.run_paper_trading(db=db, city_ids=selected_city_ids)
            counts["paper_orders_created"] = paper_result["paper_orders_created"]
            counts["paper_orders_skipped"] = paper_result["paper_orders_skipped"]
            failures.extend(_failure_items(paper_result, "failed_paper_orders"))
            self._log_step_result(
                db,
                agent_run.id,
                "paper_trading",
                "Paper trading simulation completed.",
                paper_result,
                "failed_paper_orders",
            )

            if run_evaluation_after:
                self.log_service.add_log(
                    db=db,
                    agent_run_id=agent_run.id,
                    step_name="evaluation",
                    status="skipped",
                    message="Evaluation is outside Phase 8 and was not run.",
                    metadata={"run_evaluation_after": True},
                )

            summary = self._build_city_summary(db, selected_cities)
            status = _final_status(counts=counts, failures=failures)
            message = "Agent run completed." if status == "completed" else f"Agent run {status}."
            self.log_service.update_run(
                db=db,
                agent_run=agent_run,
                status=status,
                summary=summary,
                counts=counts,
            )

            return {
                "success": status != "failed",
                "message": message,
                "agent_run_id": agent_run.id,
                "status": status,
                "cities_processed": counts["cities_processed"],
                "weather_snapshots_created": counts["weather_snapshots_created"],
                "market_snapshots_created": counts["market_snapshots_created"],
                "predictions_created": counts["predictions_created"],
                "risk_reports_created": counts["risk_reports_created"],
                "paper_orders_created": counts["paper_orders_created"],
                "paper_orders_skipped": counts["paper_orders_skipped"],
                "summary": summary,
            }
        except Exception as exc:
            self.log_service.add_log(
                db=db,
                agent_run_id=agent_run.id,
                step_name="agent_run",
                status="failed",
                message="Agent run failed.",
                error_message=str(exc),
            )
            self.log_service.update_run(
                db=db,
                agent_run=agent_run,
                status="failed",
                error_message=str(exc),
                counts=counts,
            )
            return {
                "success": False,
                "message": "Agent run failed.",
                "agent_run_id": agent_run.id,
                "status": "failed",
                "cities_processed": counts["cities_processed"],
                "weather_snapshots_created": counts["weather_snapshots_created"],
                "market_snapshots_created": counts["market_snapshots_created"],
                "predictions_created": counts["predictions_created"],
                "risk_reports_created": counts["risk_reports_created"],
                "paper_orders_created": counts["paper_orders_created"],
                "paper_orders_skipped": counts["paper_orders_skipped"],
                "summary": [],
                "error_message": str(exc),
            }

    def _finish_failed_run(self, db: Session, agent_run, counts: dict, message: str) -> dict:
        self.log_service.add_log(
            db=db,
            agent_run_id=agent_run.id,
            step_name="cities",
            status="failed",
            message=message,
        )
        self.log_service.update_run(
            db=db,
            agent_run=agent_run,
            status="failed",
            summary=[],
            error_message=message,
            counts=counts,
        )
        return {
            "success": False,
            "message": message,
            "agent_run_id": agent_run.id,
            "status": "failed",
            "cities_processed": 0,
            "weather_snapshots_created": 0,
            "market_snapshots_created": 0,
            "predictions_created": 0,
            "risk_reports_created": 0,
            "paper_orders_created": 0,
            "paper_orders_skipped": 0,
            "summary": [],
        }

    def _update_running_counts(self, db: Session, agent_run, counts: dict) -> None:
        self.log_service.update_run(
            db=db,
            agent_run=agent_run,
            status="running",
            counts=counts,
        )

    def _log_step_result(
        self,
        db: Session,
        agent_run_id: int,
        step_name: str,
        message: str,
        result: dict,
        failure_key: str,
        fallback_used: bool = False,
    ) -> None:
        failures = result.get(failure_key) or []
        status = "partial" if failures else "success"
        self.log_service.add_log(
            db=db,
            agent_run_id=agent_run_id,
            step_name=step_name,
            status=status,
            message=message,
            fallback_used=fallback_used,
            metadata=result,
        )

    def _build_city_summary(self, db: Session, cities: list[City]) -> list[dict]:
        summary = []
        for city in cities:
            prediction = _latest_prediction(db, city.id)
            risk_report = _latest_risk_report(db, city.id)
            paper_order = _latest_paper_order(db, city.id)
            summary.append(
                {
                    "city_id": city.id,
                    "city_name": city.name,
                    "model_probability": getattr(prediction, "model_probability", None),
                    "market_probability": getattr(risk_report, "market_probability", None)
                    if risk_report is not None
                    else getattr(prediction, "market_probability", None),
                    "raw_edge": getattr(risk_report, "raw_edge", None)
                    if risk_report is not None
                    else getattr(prediction, "raw_edge", None),
                    "risk_decision": getattr(risk_report, "risk_decision", None),
                    "paper_status": getattr(paper_order, "status", None),
                }
            )
        return summary


def _empty_counts() -> dict[str, int]:
    return {
        "cities_requested": 0,
        "cities_processed": 0,
        "weather_snapshots_created": 0,
        "market_snapshots_created": 0,
        "predictions_created": 0,
        "risk_reports_created": 0,
        "paper_orders_created": 0,
        "paper_orders_skipped": 0,
    }


def _select_cities(cities: list[City], city_ids: list[int] | None) -> list[City]:
    if city_ids is None:
        return cities
    requested = set(city_ids)
    return [city for city in cities if city.id in requested]


def _failure_items(result: dict, key: str) -> list[dict]:
    return list(result.get(key) or [])


def _final_status(counts: dict, failures: list[dict]) -> str:
    useful_output = any(
        counts[field] > 0
        for field in (
            "weather_snapshots_created",
            "market_snapshots_created",
            "predictions_created",
            "risk_reports_created",
            "paper_orders_created",
            "paper_orders_skipped",
        )
    )
    if not useful_output:
        return "failed"
    if failures:
        return "partial"
    return "completed"


def _latest_prediction(db: Session, city_id: int) -> Prediction | None:
    return (
        db.query(Prediction)
        .filter(Prediction.city_id == city_id)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .first()
    )


def _latest_risk_report(db: Session, city_id: int) -> RiskReport | None:
    return (
        db.query(RiskReport)
        .filter(RiskReport.city_id == city_id)
        .order_by(RiskReport.created_at.desc(), RiskReport.id.desc())
        .first()
    )


def _latest_paper_order(db: Session, city_id: int) -> PaperOrder | None:
    return (
        db.query(PaperOrder)
        .filter(PaperOrder.city_id == city_id)
        .order_by(PaperOrder.created_at.desc(), PaperOrder.id.desc())
        .first()
    )
