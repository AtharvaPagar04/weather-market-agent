from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.alert_service import AlertService


router = APIRouter()


class AlertRequest(BaseModel):
    dry_run: bool = True


@router.get("/alerts/status")
def get_alert_status(db: Session = Depends(get_db)) -> dict:
    return AlertService(db).get_status()


@router.post("/alerts/test")
def send_test_alert(request: AlertRequest, db: Session = Depends(get_db)) -> dict:
    return AlertService(db).send_test_alert(dry_run=request.dry_run)


@router.post("/alerts/latest-run")
def send_latest_run_alert(request: AlertRequest, db: Session = Depends(get_db)) -> dict:
    return AlertService(db).send_latest_run_alert(dry_run=request.dry_run)
