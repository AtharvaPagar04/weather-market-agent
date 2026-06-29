import json
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.weather_market_agent import WeatherMarketAgent
from app.database import get_db
from app.services.agent_log_service import AgentLogService
from app.services.agent_orchestration_service import AgentOrchestrationService


router = APIRouter()


class AgentRunRequest(BaseModel):
    city_ids: list[int] | None = None
    force_mock_markets: bool = False
    run_evaluation_after: bool = False


@router.post("/agent/run")
def run_agent(request: AgentRunRequest, db: Session = Depends(get_db)) -> dict:
    if request.run_evaluation_after:
        return AgentOrchestrationService().run_full_pipeline(
            db=db,
            city_ids=request.city_ids,
            force_mock_markets=request.force_mock_markets,
            run_evaluation_after=request.run_evaluation_after,
        )
    return WeatherMarketAgent().run(
        db=db,
        city_ids=request.city_ids,
        force_mock_markets=request.force_mock_markets,
    )


@router.get("/agent/runs")
def list_agent_runs(status: str | None = None, db: Session = Depends(get_db)) -> list[dict]:
    runs = AgentLogService().list_runs(db=db, status=status)
    return [
        {
            "id": run.id,
            "run_id": run.run_id,
            "run_type": run.run_type,
            "status": run.status,
            "cities_requested": run.cities_requested,
            "cities_processed": run.cities_processed,
            "weather_snapshots_created": run.weather_snapshots_created,
            "market_snapshots_created": run.market_snapshots_created,
            "predictions_created": run.predictions_created,
            "risk_reports_created": run.risk_reports_created,
            "paper_orders_created": run.paper_orders_created,
            "paper_orders_skipped": run.paper_orders_skipped,
            "summary": _parse_json(run.summary_json, []),
            "error_message": run.error_message,
            "started_at": _serialize_datetime(run.started_at),
            "finished_at": _serialize_datetime(run.finished_at),
            "created_at": _serialize_datetime(run.created_at),
        }
        for run in runs
    ]


@router.get("/agent/logs")
def list_agent_logs(
    agent_run_id: int | None = None,
    city_id: int | None = None,
    status: str | None = None,
    step_name: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    logs = AgentLogService().list_logs(
        db=db,
        agent_run_id=agent_run_id,
        city_id=city_id,
        status=status,
        step_name=step_name,
    )
    return [
        {
            "id": log.id,
            "agent_run_id": log.agent_run_id,
            "city_id": log.city_id,
            "city_name": log.city_name,
            "step_name": log.step_name,
            "status": log.status,
            "message": log.message,
            "fallback_used": log.fallback_used,
            "error_message": log.error_message,
            "metadata": _parse_json(log.metadata_json or log.payload_json, {}),
            "created_at": _serialize_datetime(log.created_at),
        }
        for log in logs
    ]


def _parse_json(value: str | None, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
