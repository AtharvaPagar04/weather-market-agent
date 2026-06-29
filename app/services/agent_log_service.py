import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.db_models import AgentRun, AgentRunLog


FINAL_STATUSES = {"completed", "partial", "failed"}


class AgentLogService:
    def create_run(
        self,
        db: Session,
        run_type: str,
        cities_requested: int,
    ) -> AgentRun:
        agent_run = AgentRun(
            run_id=str(uuid4()),
            run_type=run_type,
            status="running",
            cities_requested=cities_requested,
            cities_processed=0,
            weather_snapshots_created=0,
            market_snapshots_created=0,
            predictions_created=0,
            risk_reports_created=0,
            paper_orders_created=0,
            paper_orders_skipped=0,
            summary_json="[]",
        )
        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)
        return agent_run

    def update_run(
        self,
        db: Session,
        agent_run: AgentRun,
        status: str,
        summary: dict | list | None = None,
        error_message: str | None = None,
        counts: dict | None = None,
    ) -> AgentRun:
        agent_run.status = status
        if status in FINAL_STATUSES:
            agent_run.finished_at = datetime.now(UTC).replace(tzinfo=None)
        if summary is not None:
            agent_run.summary_json = json.dumps(summary, sort_keys=True)
        if error_message is not None:
            agent_run.error_message = error_message
        for field, value in (counts or {}).items():
            if hasattr(agent_run, field):
                setattr(agent_run, field, value)

        db.add(agent_run)
        db.commit()
        db.refresh(agent_run)
        return agent_run

    def add_log(
        self,
        db: Session,
        agent_run_id: int,
        step_name: str,
        status: str,
        message: str,
        city_id: int | None = None,
        city_name: str | None = None,
        fallback_used: bool = False,
        error_message: str | None = None,
        metadata: dict | None = None,
    ) -> AgentRunLog:
        metadata_json = json.dumps(metadata or {}, sort_keys=True)
        log = AgentRunLog(
            agent_run_id=agent_run_id,
            city_id=city_id,
            city_name=city_name,
            step_name=step_name,
            status=status,
            message=message,
            fallback_used=fallback_used,
            error_message=error_message,
            metadata_json=metadata_json,
            payload_json=metadata_json,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def list_runs(self, db: Session, status: str | None = None) -> list[AgentRun]:
        query = db.query(AgentRun)
        if status is not None:
            query = query.filter(AgentRun.status == status)
        return query.order_by(AgentRun.started_at.desc(), AgentRun.id.desc()).all()

    def list_logs(
        self,
        db: Session,
        agent_run_id: int | None = None,
        city_id: int | None = None,
        status: str | None = None,
        step_name: str | None = None,
    ) -> list[AgentRunLog]:
        query = db.query(AgentRunLog)
        if agent_run_id is not None:
            query = query.filter(AgentRunLog.agent_run_id == agent_run_id)
        if city_id is not None:
            query = query.filter(AgentRunLog.city_id == city_id)
        if status is not None:
            query = query.filter(AgentRunLog.status == status)
        if step_name is not None:
            query = query.filter(AgentRunLog.step_name == step_name)
        return query.order_by(AgentRunLog.created_at.asc(), AgentRunLog.id.asc()).all()
