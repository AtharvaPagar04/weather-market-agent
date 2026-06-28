from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.config import get_settings


settings = get_settings()

app = FastAPI(title=settings.APP_NAME)
app.include_router(health_router)

