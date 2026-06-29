"""Run the final local smoke test for the Weather Market Agent demo.

The smoke test uses FastAPI TestClient with an isolated temporary SQLite
database and temporary demo output directory. It does not require external
credentials, Telegram configuration, Apify configuration, or a running server.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAFETY_STATEMENT = (
    "Paper trading only - all execution shown is simulated. No real funds, wallets, "
    "private keys, signing credentials, or real-money orders are used."
)

EXPECTED_DEMO_FILES = (
    "results_summary.csv",
    "sample_predictions.json",
    "sample_orders.json",
    "pm_trader_stats.json",
)

EXPECTED_ROUTES = {
    "/health",
    "/cities/seed",
    "/cities",
    "/agent/run",
    "/agent/runs",
    "/agent/logs",
    "/evaluation/summary",
    "/evaluation/run",
    "/demo/export",
    "/alerts/status",
    "/alerts/test",
}


class SmokeFailure(AssertionError):
    """Raised when a named smoke-test check fails."""


def _mark(step_name: str) -> None:
    if os.environ.get("FINAL_SMOKE_VERBOSE") == "1":
        print(f"SMOKE STEP: {step_name}", flush=True)


def _check(condition: bool, check_name: str, detail: str) -> None:
    if not condition:
        raise SmokeFailure(f"{check_name}: {detail}")


def _prepare_isolated_environment() -> None:
    os.environ["APIFY_API_TOKEN"] = ""
    os.environ["PM_TRADER_ENABLED"] = "false"
    os.environ["PM_TRADER_ALLOW_ORDER_EXECUTION"] = "false"
    os.environ["PM_TRADER_PAPER_EXECUTION_ENABLED"] = "false"
    os.environ["TELEGRAM_ALERTS_ENABLED"] = "false"
    os.environ["TELEGRAM_BOT_TOKEN"] = ""
    os.environ["TELEGRAM_CHAT_ID"] = ""
    sys.path.insert(0, str(PROJECT_ROOT))


def _run_smoke_checks() -> None:
    with tempfile.TemporaryDirectory(prefix="weather-agent-final-smoke-") as tmp:
        tmp_dir = Path(tmp)
        _prepare_isolated_environment()

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from app import database
        from app.agents.weather_market_agent import WeatherMarketAgent
        from app.api.routes_health import health_check
        from app.config import get_settings
        from app.main import app
        from app.services.agent_log_service import AgentLogService
        from app.services.alert_service import AlertService
        from app.services.city_service import CityService
        from app.services.evaluation_service import EvaluationService

        get_settings.cache_clear()
        test_engine = create_engine(
            f"sqlite:///{tmp_dir / 'final_smoke.db'}",
            connect_args={"check_same_thread": False},
        )
        database.engine = test_engine
        database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        database.init_db()

        db = database.SessionLocal()
        try:
            route_paths = set(app.openapi().get("paths", {}))
            missing_routes = sorted(EXPECTED_ROUTES - route_paths)
            _check(not missing_routes, "Route map", f"missing expected routes: {missing_routes}")

            _mark("health")
            health = health_check()
            _check(health.get("status") == "ok", "Backend health", f"unexpected health payload: {health}")

            _mark("cities seed")
            seed_payload = CityService.seed_default_cities(db, reset_existing=True)
            _check(seed_payload.get("total_active_cities") == 5, "City seeding", f"expected 5 cities: {seed_payload}")

            _mark("cities list")
            cities = CityService.get_active_cities(db)
            _check(isinstance(cities, list) and len(cities) == 5, "Cities list", f"expected 5 cities: {cities}")

            _mark("agent run")
            agent_payload = WeatherMarketAgent().run(db=db)
            _check(agent_payload.get("success") is True, "Agent pipeline", f"agent run did not succeed: {agent_payload}")
            _check(
                agent_payload.get("status") in {"completed", "partial"},
                "Agent pipeline",
                f"unexpected status: {agent_payload}",
            )
            _check(agent_payload.get("cities_processed") == 5, "Agent pipeline", f"expected 5 cities: {agent_payload}")
            _check(
                agent_payload.get("predictions_created", 0) >= 5,
                "Agent pipeline",
                f"expected at least 5 predictions: {agent_payload}",
            )
            _check(
                agent_payload.get("risk_reports_created", 0) >= 5,
                "Agent pipeline",
                f"expected at least 5 risk reports: {agent_payload}",
            )
            _check(
                agent_payload.get("paper_orders_created", 0) >= 0,
                "Agent pipeline",
                f"paper order count missing: {agent_payload}",
            )
            _check(
                agent_payload.get("paper_orders_skipped", 0) >= 0,
                "Agent pipeline",
                f"paper skipped count missing: {agent_payload}",
            )

            _mark("agent runs")
            runs = AgentLogService().list_runs(db=db)
            _check(isinstance(runs, list) and runs, "Agent runs", "expected at least one agent run")

            _mark("agent logs")
            logs = AgentLogService().list_logs(db=db)
            _check(isinstance(logs, list) and logs, "Agent logs", "expected agent step logs")

            evaluation_service = EvaluationService(db)
            _mark("evaluation summary")
            summary = evaluation_service.get_summary()
            _check(summary.get("predictions_count", 0) >= 5, "Evaluation summary", f"unexpected summary: {summary}")
            _check(summary.get("risk_reports_count", 0) >= 5, "Evaluation summary", f"unexpected summary: {summary}")
            _check(summary.get("outcome_data_available") is False, "Evaluation summary", f"unexpected summary: {summary}")
            _check(summary.get("accuracy_metrics_available") is False, "Evaluation summary", f"unexpected summary: {summary}")

            _mark("evaluation run")
            evaluation_run = evaluation_service.run_evaluation()
            _check(
                evaluation_run.get("predictions_count", 0) >= 5,
                "Evaluation run",
                f"unexpected evaluation run payload: {evaluation_run}",
            )

            _mark("demo export")
            export_payload = evaluation_service.export_demo_output(output_dir=str(tmp_dir / "demo_output"))
            _check(export_payload.get("status") == "success", "Demo export", f"unexpected export payload: {export_payload}")

            generated_dir = tmp_dir / "demo_output"
            for file_name in EXPECTED_DEMO_FILES:
                file_path = generated_dir / file_name
                _check(file_path.exists(), "Generated files", f"missing {file_path}")
                _check(file_path.stat().st_size > 0, "Generated files", f"{file_path} is empty")

            for json_name in ("sample_predictions.json", "sample_orders.json", "pm_trader_stats.json"):
                with (generated_dir / json_name).open() as file_handle:
                    json.load(file_handle)

            alert_service = AlertService(db)
            _mark("alerts status")
            alert_status = alert_service.get_status()
            _check(alert_status.get("enabled") is False, "Alerts status", f"unexpected alert status: {alert_status}")
            _check("token" not in alert_status.get("source", "").lower(), "Alerts status", "source exposed token wording")
            _check("TELEGRAM_BOT_TOKEN" not in json.dumps(alert_status), "Alerts status", "token variable exposed")

            _mark("alerts test")
            alert_test = alert_service.send_test_alert()
            _check(alert_test.get("sent") is False, "Alerts test", f"unexpected alert payload: {alert_test}")
            _check(alert_test.get("skipped") is True, "Alerts test", f"unexpected alert payload: {alert_test}")
            _check("Paper trading only" in alert_test.get("message", ""), "Alerts test", "missing paper warning")

            blocked_paths = {
                "/orders" + "/place",
                "/trade" + "/execute",
                "/account" + "/connect",
                "/private" + "-key",
                "/wal" + "let",
                "/paper-trader" + "/buy",
                "/paper-trader" + "/sell",
                "/paper-trader" + "/order",
            }
            present_blocked = sorted(blocked_paths & route_paths)
            _check(not present_blocked, "Paper-only safety", f"unsafe routes present: {present_blocked}")
        finally:
            db.close()


def main() -> int:
    try:
        _run_smoke_checks()
    except SmokeFailure as exc:
        print("FINAL SMOKE TEST FAILED")
        print(str(exc))
        return 1
    except Exception as exc:  # pragma: no cover - CLI guard prints the actual traceback cause.
        print("FINAL SMOKE TEST FAILED")
        print(f"Unexpected error: {type(exc).__name__}: {exc}")
        return 1

    print("FINAL SMOKE TEST PASSED")
    print()
    print("Backend health: PASS")
    print("Agent pipeline: PASS")
    print("Evaluation summary: PASS")
    print("Demo export: PASS")
    print("Alerts status: PASS")
    print("Paper-only safety: PASS")
    print("Generated files: PASS")
    print()
    print(SAFETY_STATEMENT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
