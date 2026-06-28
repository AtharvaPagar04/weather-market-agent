from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schemas import CityRead, CitySeedRequest, CitySeedResponse
from app.services.city_service import CityService


router = APIRouter()


@router.get("/cities", response_model=list[CityRead])
def list_cities(db: Session = Depends(get_db)) -> list[CityRead]:
    return CityService.get_active_cities(db)


@router.post("/cities/seed", response_model=CitySeedResponse)
def seed_cities(request: CitySeedRequest, db: Session = Depends(get_db)) -> dict[str, int | str | bool]:
    return CityService.seed_default_cities(db, reset_existing=request.reset_existing)
