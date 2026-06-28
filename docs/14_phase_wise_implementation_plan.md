# 14 - Phase-Wise Implementation Plan

## Purpose

This document defines the phase-by-phase build plan for the Weather-Market Research Agent MVP after adopting `polymarket-paper-trader` as the primary market-data and paper execution layer.

## Current MVP Decision

Implementation should build the weather pipeline, market integration, prediction model, risk engine, pm-trader paper execution, local DB audit mirror, dashboard, and evaluation in small verifiable phases.

No code is implemented by this documentation task.

## Implementation Notes

### Core Architecture Terms

Required integration terms for phase-wise implementation:

```txt
polymarket-paper-trader
PolymarketPaperTraderAdapter
PolymarketMarketTool
PolymarketPaperTradeTool
```

### Phase 0 - Documentation and Scope Lock

Goal:

```txt
Finalize MVP documentation and confirm paper-trading-only boundaries.
```

Deliverables:

```txt
docs/00_project_plan.md
docs/01_architecture.md
docs/04_api_design.md
docs/06_market_data_design.md
docs/10_paper_trading.md
docs/14_phase_wise_implementation_plan.md
```

### Phase 1 - Backend Foundation

Goal:

```txt
Create the FastAPI skeleton, config loading, basic logging, and health endpoint.
```

Later files:

```txt
app/main.py
app/config.py
app/api/routes_health.py
```

City endpoints may be added in Phase 1 only as a static config-based placeholder. DB-backed city endpoints belong to Phase 2 after the cities table exists.

Validation:

```txt
GET /health returns healthy status
Config loads safe defaults
No database initialization is required yet
```

### Phase 2 - Data Layer

Goal:

```txt
Create SQLite and SQLAlchemy persistence for local audit records.
```

Later tables:

```txt
cities
weather_snapshots
market_snapshots
predictions
risk_reports
paper_orders
positions
evaluation_results
agent_runs
agent_run_logs
```

Later files:

```txt
app/api/routes_cities.py
app/services/city_service.py
```

`agent_runs` stores one row per complete agent run.
`agent_run_logs` stores step-by-step events inside each run.

Validation:

```txt
GET /cities returns the five configured MVP cities after database initialization or seeding
POST /cities/seed creates the five MVP cities without duplicates
```

### Phase 3 - Weather Data Pipeline

Goal:

```txt
Fetch and normalize global, local, and Apify weather data.
```

Later files:

```txt
app/tools/global_weather_tool.py
app/tools/local_weather_tool.py
app/tools/apify_weather_tool.py
app/tools/weather_normalizer.py
app/services/weather_service.py
```

### Phase 4 - Market Data Pipeline

Goal:

```txt
Prepare market snapshot normalization and city-to-market matching.
```

Later files:

```txt
app/services/market_service.py
app/tools/market_normalizer.py
app/tools/mock_market_data.py
```

Mock market data is fallback-only after pm-trader integration.

### Phase 4.5 — Polymarket Paper Trader Integration

Goal:

```txt
Integrate polymarket-paper-trader for market search, price/order-book access, portfolio/history/stats access, and prepare paper execution adapter methods. Actual pm-trader paper buy/sell execution is enabled only in Phase 7 after RiskService approval exists.
```

Files to create later:

```txt
app/integrations/polymarket_paper_trader_client.py
app/tools/polymarket_market_tool.py
app/tools/polymarket_paper_trade_tool.py
tests/test_polymarket_paper_trader_client.py
tests/test_polymarket_market_tool.py
tests/test_polymarket_paper_trade_tool.py
```

Implementation tasks:

```txt
1. Add dependency polymarket-paper-trader.
2. Create adapter wrapper.
3. Initialize paper account.
4. Search weather markets.
5. Fetch price and order book.
6. Normalize pm-trader market data into market_snapshots.
7. Create adapter methods for paper buy/sell, but do not enable them in the workflow until Phase 7.
8. Prepare local audit record mapping for later paper execution.
9. Read portfolio/history/stats for dashboard.
10. Add fallback to mock markets if pm-trader is unavailable.
```

Portfolio/history/stats can be read in Phase 4.5, but paper buy/sell workflow is activated only after risk approval logic exists.

Manual validation commands:

```bash
pip install polymarket-paper-trader
pm-trader init --balance 10000
pm-trader markets search "weather"
pm-trader portfolio
pm-trader stats
```

If a real weather market slug is found:

```bash
pm-trader price <market-slug>
pm-trader book <market-slug> --depth 5
```

Backend validation:

```txt
GET /markets/search?query=weather returns structured results
GET /markets/{slug}/price returns price data
GET /markets/{slug}/book returns order-book data
GET /paper-trades/portfolio returns pm-trader portfolio
GET /paper-trades/stats returns pm-trader stats
Phase 4.5 prepares paper execution methods, but does not enable paper buy/sell workflow before RiskService approval exists.
```

Safety validation:

```txt
No private key config exists
No wallet config exists
No real execution endpoint exists
Risk rejection never calls pm-trader buy/sell
All dashboard labels say paper/simulated
```

### Phase 5 - Prediction Model

Goal:

```txt
Generate explainable probabilities from normalized weather signals only.
```

Later files:

```txt
app/services/prediction_service.py
app/tools/forecast_tool.py
```

### Phase 6 - Risk Management

Goal:

```txt
Implement edge calculation, risk gates, confidence checks, order-book liquidity checks, exposure caps, and fractional Kelly sizing before any paper execution can happen.
```

Later files:

```txt
app/services/risk_service.py
app/tools/risk_tool.py
tests/test_risk_service.py
tests/test_risk_tool.py
```

Validation:

```txt
Risk rejection never calls pm-trader buy/sell
trade_allowed must be true before paper execution
market_slug must exist before paper execution
tradeable_edge is calculated before sizing
```

### Phase 7 - Paper Execution

Goal:

```txt
Use polymarket-paper-trader for paper buy/sell only after RiskService approval and store local audit records.
```

Later files:

```txt
app/services/paper_trading_service.py
app/services/position_service.py
app/tools/polymarket_paper_trade_tool.py
tests/test_paper_trading_service.py
tests/test_polymarket_paper_trade_tool.py
```

Validation:

```txt
Approved risk report can create a pm-trader paper buy or paper sell
Rejected risk report creates local paper_order_skipped only
Local audit record is created for created and skipped paper decisions
pm_trader_result_json is stored when available
```

### Phase 8 - Hermes Agent Orchestration

Goal:

```txt
Use Hermes WeatherMarketAgent to orchestrate already-tested tools and services.
```

Later files:

```txt
app/agents/weather_market_agent.py
app/services/agent_log_service.py
tests/test_agent_run.py
tests/test_agent_logs.py
```

Validation:

```txt
Agent calls WeatherTool, PolymarketMarketTool, ForecastTool, RiskTool, PolymarketPaperTradeTool, and ExplanationTool in order
Agent cannot bypass RiskTool
Agent cannot call pm-trader paper buy/sell directly
Every city run creates audit logs
```

### Phase 9 - Streamlit Dashboard

Goal:

```txt
Show weather signals, Polymarket market data, risk decisions, pm-trader portfolio/history/stats, and local audit orders.
```

Later files:

```txt
dashboard/streamlit_app.py
dashboard/pages/overview.py
dashboard/pages/paper_trades.py
dashboard/pages/risk_dashboard.py
dashboard/pages/results.py
```

### Phase 10 - Statistical Evaluation

Goal:

```txt
Generate assignment metrics and combine pm-trader stats with local evaluator outputs.
```

Later outputs:

```txt
demo_output/results_summary.csv
demo_output/sample_predictions.json
demo_output/sample_orders.json
demo_output/pm_trader_stats.json
```

### Phase 11 - Polish and Submission

Goal:

```txt
Make the project internship-ready with README, examples, screenshots, and demo video.
```

### Service-First Rule

The Hermes Agent should be implemented after the core services are individually working.

Correct implementation order:

```txt
services first
tools second
agent orchestration third
dashboard after backend flow exists
```

Reason:

```txt
The agent should orchestrate tested services, not contain untested business logic.
```

## Acceptance Checklist

- [ ] `Phase 4.5 — Polymarket Paper Trader Integration` is documented.
- [ ] `app/integrations/polymarket_paper_trader_client.py` is listed.
- [ ] `pm-trader markets search "weather"` is documented.
- [ ] `GET /paper-trades/stats` is documented.
- [ ] `Risk rejection never calls pm-trader buy/sell` is documented.
- [ ] Mock market data is fallback-only.
- [ ] No implementation code is created by this documentation task.

---

## Resource-Informed Phase Additions

### Phase 1.5 - Reference Resource Mapping

Tasks:

```txt
Reference resource mapping
Create docs/15_reference_resources_analysis.md
Update docs based on attached resources
Validate MVP boundary
```

Validation:

```txt
Inputs exist
Resource usage is documented
No real-money credentials exist
```

### Phase 2.x - Apify Weather Ingestion Design

Tasks:

```txt
Add Apify weather ingestion design
Normalize Apify output
Compare Apify against official/local sources
```

Validation:

```txt
Inputs exist
Outputs are normalized
Source confidence rules are documented
```

### Phase 3.x - Probability Buckets and Confidence

Tasks:

```txt
Add probability bucket design
Add confidence interval and uncertainty penalty
Map probability buckets to market buckets
```

Validation:

```txt
Inputs exist
Outputs are normalized
Risk gates are checked
```

### Phase 4.5 - Polymarket Paper Trader Integration Detail

Tasks:

```txt
polymarket-paper-trader integration
pm-trader init --balance 10000
market search
price/book retrieval
paper buy/sell
portfolio/history/stats
local audit mirror
```

Validation:

```txt
Inputs exist
Outputs are normalized
Risk gates are checked
Paper trade is auditable
No real-money credentials exist
Dashboard values match backend/audit state
```

### Phase 5.x - Detector-Based Hermes Agent Orchestration

Tasks:

```txt
Detector-based Hermes agent orchestration
structured JSON signal output
risk-gated paper action
```

Validation:

```txt
Inputs exist
Outputs are normalized
Risk gates are checked
Paper trade is auditable
```

### Phase 6.x - Terminal-Style Dashboard MVP

Tasks:

```txt
Terminal-style dashboard MVP
Market Watch
Probability Tracker
Edge Matrix
Paper Portfolio
Transaction Feed
```

Validation:

```txt
Dashboard values match backend/audit state
No real-money credentials exist
```
