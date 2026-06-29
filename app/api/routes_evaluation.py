from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.evaluation_service import EvaluationService
from app.database import get_db

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.get("/summary")
def get_evaluation_summary(db: Session = Depends(get_db)):
    service = EvaluationService(db)
    return service.get_summary()

@router.post("/run")
def run_evaluation(db: Session = Depends(get_db)):
    service = EvaluationService(db)
    return service.run_evaluation()

@router.post("/export")
def export_demo(db: Session = Depends(get_db)):
    service = EvaluationService(db)
    return service.export_demo_output()

# Also map /demo/export to match the requirements strictly
demo_router = APIRouter(prefix="/demo", tags=["Demo"])

@demo_router.post("/export")
def demo_export(db: Session = Depends(get_db)):
    service = EvaluationService(db)
    return service.export_demo_output()
