from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CityRead(BaseModel):
    id: int
    name: str
    country: str
    country_code: str
    timezone: str
    latitude: float
    longitude: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CitySeedRequest(BaseModel):
    reset_existing: bool = False


class CitySeedResponse(BaseModel):
    success: bool
    message: str
    cities_created: int
    total_active_cities: int


class ActionResponse(BaseModel):
    success: bool
    message: str
