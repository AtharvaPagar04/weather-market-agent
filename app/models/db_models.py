from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("name", "country_code", name="uq_city_name_country_code"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    country = Column(String(120), nullable=False)
    country_code = Column(String(8), nullable=False)
    timezone = Column(String(80), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    source = Column(String(120), nullable=False)
    source_confidence = Column(Float, nullable=True)
    forecast_for = Column(DateTime, nullable=True)
    observed_at = Column(DateTime, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    rain_probability = Column(Float, nullable=True)
    wind_speed_kph = Column(Float, nullable=True)
    pressure_hpa = Column(Float, nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    condition = Column(String(120), nullable=True)
    raw_payload_json = Column(Text, nullable=True)
    status = Column(String(40), nullable=False, default="ok")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    market_id = Column(String(160), nullable=True)
    market_slug = Column(String(240), nullable=False, index=True)
    question = Column(Text, nullable=False)
    outcome_type = Column(String(80), nullable=True)
    yes_price = Column(Float, nullable=True)
    no_price = Column(Float, nullable=True)
    implied_probability = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    liquidity = Column(Float, nullable=True)
    end_date = Column(DateTime, nullable=True)
    source_type = Column(String(80), nullable=True)
    source_name = Column(String(120), nullable=True)
    matched_query = Column(Text, nullable=True)
    order_book_available = Column(Boolean, nullable=False, default=False)
    best_bid = Column(Float, nullable=True)
    best_ask = Column(Float, nullable=True)
    midpoint = Column(Float, nullable=True)
    spread = Column(Float, nullable=True)
    pm_trader_source = Column(String(120), nullable=True)
    raw_payload_json = Column(Text, nullable=True)
    fetched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    market_snapshot_id = Column(Integer, ForeignKey("market_snapshots.id"), nullable=True, index=True)
    model_version = Column(String(80), nullable=False)
    prediction_type = Column(String(80), nullable=False)
    model_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    source_agreement = Column(Float, nullable=True)
    global_signal = Column(Float, nullable=True)
    local_signal = Column(Float, nullable=True)
    apify_signal = Column(Float, nullable=True)
    recent_trend_signal = Column(Float, nullable=True)
    source_confidence_signal = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)
    generated_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)
    market_snapshot_id = Column(Integer, ForeignKey("market_snapshots.id"), nullable=True, index=True)
    market_slug = Column(String(240), nullable=False, index=True)
    model_probability = Column(Float, nullable=False)
    market_probability = Column(Float, nullable=True)
    raw_edge = Column(Float, nullable=True)
    tradeable_edge = Column(Float, nullable=True)
    spread_cost = Column(Float, nullable=True)
    uncertainty_penalty = Column(Float, nullable=True)
    liquidity_penalty = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    liquidity_score = Column(Float, nullable=True)
    recommended_side = Column(String(20), nullable=True)
    recommended_size = Column(Float, nullable=True)
    trade_allowed = Column(Boolean, nullable=False, default=False)
    blocked_reason = Column(Text, nullable=True)
    risk_level = Column(String(40), nullable=True)
    risk_decision = Column(String(80), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id = Column(Integer, primary_key=True, index=True)
    risk_report_id = Column(Integer, ForeignKey("risk_reports.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True, index=True)
    market_snapshot_id = Column(Integer, ForeignKey("market_snapshots.id"), nullable=True, index=True)
    market_slug = Column(String(240), nullable=False, index=True)
    side = Column(String(20), nullable=False)
    outcome = Column(String(120), nullable=True)
    requested_amount = Column(Float, nullable=False)
    simulated_price = Column(Float, nullable=True)
    status = Column(String(40), nullable=False, default="created")
    paper_execution_source = Column(String(120), nullable=True)
    pm_trader_account = Column(String(160), nullable=True)
    pm_trader_order_id = Column(String(160), nullable=True)
    pm_trader_result_json = Column(Text, nullable=True)
    audit_sync_status = Column(String(80), nullable=True)
    audit_sync_error = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    market_slug = Column(String(240), nullable=False, index=True)
    side = Column(String(20), nullable=False)
    outcome = Column(String(120), nullable=True)
    total_size = Column(Float, nullable=False, default=0.0)
    average_price = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=False, default=0.0)
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    paper_execution_source = Column(String(120), nullable=True)
    status = Column(String(40), nullable=False, default="open")
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_run_id = Column(String(160), nullable=False, index=True)
    metric_name = Column(String(120), nullable=False)
    metric_value = Column(Float, nullable=True)
    metric_group = Column(String(120), nullable=True)
    sample_size = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(160), nullable=False, unique=True, index=True)
    status = Column(String(40), nullable=False)
    started_at = Column(DateTime, nullable=False, default=utc_now)
    finished_at = Column(DateTime, nullable=True)
    cities_processed = Column(Integer, nullable=False, default=0)
    predictions_created = Column(Integer, nullable=False, default=0)
    risk_reports_created = Column(Integer, nullable=False, default=0)
    paper_orders_created = Column(Integer, nullable=False, default=0)
    paper_orders_skipped = Column(Integer, nullable=False, default=0)
    summary_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)


class AgentRunLog(Base):
    __tablename__ = "agent_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, index=True)
    step_name = Column(String(120), nullable=False)
    status = Column(String(40), nullable=False)
    message = Column(Text, nullable=True)
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
