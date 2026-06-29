from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import database
from app.api.routes_agent import router as agent_router
from app.api.routes_alerts import router as alerts_router
from app.api.routes_cities import router as cities_router
from app.api.routes_health import router as health_router
from app.api.routes_markets import router as markets_router
from app.api.routes_paper_trades import router as paper_trades_router
from app.api.routes_paper_trader import router as paper_trader_router
from app.api.routes_positions import router as positions_router
from app.api.routes_predictions import router as predictions_router
from app.api.routes_risk import router as risk_router
from app.api.routes_weather import router as weather_router
from app.api.routes_evaluation import router as evaluation_router, demo_router
from app.config import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    database.init_db()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(health_router)
app.include_router(cities_router)
app.include_router(weather_router)
app.include_router(markets_router)
app.include_router(paper_trader_router)
app.include_router(predictions_router)
app.include_router(risk_router)
app.include_router(paper_trades_router)
app.include_router(positions_router)
app.include_router(agent_router)
app.include_router(evaluation_router)
app.include_router(demo_router)
app.include_router(alerts_router)
