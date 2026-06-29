from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Weather Market Agent"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./weather_agent.db"

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = ""

    APIFY_API_TOKEN: str = ""

    PM_TRADER_ENABLED: bool = False
    PM_TRADER_ALLOW_ORDER_EXECUTION: bool = False
    PM_TRADER_USE_MOCK_FALLBACK: bool = True
    PM_TRADER_COMMAND: str = "pm-trader"
    PM_TRADER_TIMEOUT_SECONDS: int = 10

    USE_MOCK_MARKETS: bool = True
    USE_MOCK_WEATHER: bool = False

    INITIAL_BANKROLL: float = 1000.0
    MIN_CONFIDENCE: float = 0.60
    MIN_EDGE: float = 0.05
    MAX_TRADE_RISK_PCT: float = 0.02
    MAX_TOTAL_EXPOSURE_PCT: float = 0.10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
