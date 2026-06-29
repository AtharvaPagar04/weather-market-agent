# Weather Market Agent

Weather Market Agent is a local, paper-trading-only research system for weather-related prediction markets. It collects deterministic weather signals for five cities, maps them to mock or read-only Polymarket-style market data, generates baseline rain probabilities, applies conservative risk checks, simulates paper decisions, and exports demo-ready evaluation artifacts.

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

## Assignment Mapping

The project demonstrates an agentic workflow for a market-research assignment:

- Weather data collection and normalization across global, local, and Apify-style sources.
- Market data matching through a mock fallback pipeline and a safe read-only polymarket-paper-trader boundary.
- Explainable prediction generation from weather signals.
- Risk management before any paper decision.
- Paper-trading simulation with local audit records.
- Streamlit dashboard for demo review.
- Statistical evaluation and demo output exports.

## What The System Does

The backend runs a complete local pipeline for five default cities:

- Mumbai
- London
- New York
- Tokyo
- Sydney

For each city, it refreshes weather snapshots, refreshes weather-market snapshots, generates a model probability, compares the model probability with market-implied probability, creates a risk report, and records a simulated paper decision. If a risk decision is not approved for a paper order, the system records a skipped paper decision with the reason.

## Architecture Overview

The system is service-first. FastAPI routes call services, and the agent orchestration layer calls those same services in order.

- `WeatherService`: collects deterministic global/local weather data and Apify fallback status.
- `MarketService`: creates mock market snapshots and keeps the read-only pm-trader adapter boundary.
- `PredictionService`: creates baseline model predictions.
- `RiskService`: calculates edge, penalties, risk gates, and Kelly-style sizing for paper analysis.
- `PaperTradingService`: records simulated paper orders or skipped paper decisions.
- `AgentOrchestrationService`: runs the full backend pipeline and stores agent run logs.
- `EvaluationService`: summarizes counts and exports demo artifacts.

Data is stored in SQLite through SQLAlchemy models. The local database defaults to `weather_agent.db`.

## Agent Pipeline Flow

`POST /agent/run` performs:

1. Load or seed the five default cities.
2. Refresh weather snapshots.
3. Refresh market snapshots.
4. Generate predictions.
5. Analyze risk.
6. Run paper-trading simulation.
7. Store agent run and step logs.
8. Return a city-level summary.

The agent does not bypass risk management and does not directly create paper orders. Paper decisions flow through `PaperTradingService`.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pytest
- Streamlit
- Deterministic mock tools for local, network-free testing

## Features Completed

- 5-city weather market pipeline
- Global/local/Apify weather source flow
- Polymarket/mock market pipeline
- Prediction model
- Risk management / Kelly-style sizing
- Paper trading simulation
- Streamlit dashboard
- Evaluation metrics
- Demo output exports

## Setup

Create or reuse the local virtual environment, then install requirements:

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

If `.venv` does not exist yet, create it first with your preferred Python environment tool.

Optional environment variables can be copied from `.env.example`. No credentials are required for the deterministic local demo.

## Run Tests

```bash
./.venv/bin/python -m pytest tests/*.py
./.venv/bin/python scripts/validate_docs_consistency.py
./.venv/bin/python -m pytest tests/test_docs_consistency.py
```

## Run Backend

```bash
./.venv/bin/python -m uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run Dashboard

In a second terminal:

```bash
BACKEND_API_URL=http://127.0.0.1:8000 ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py
```

Use the sidebar to run the agent pipeline and navigate:

- Overview
- Predictions
- Risk Dashboard
- Paper Trades
- Agent Logs
- Results / Evaluation

## Run Full Agent Pipeline

With the backend running:

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected local demo behavior:

- 5 cities processed
- 15 weather snapshots
- 5 market snapshots
- 5 predictions
- 5 risk reports
- Paper orders created or skipped depending on risk decision
- Agent status may be `partial` when Apify is not configured, because the Apify source records a safe failed snapshot while global/local weather continue.

## Export Demo Outputs

With the backend running:

```bash
curl -X POST http://127.0.0.1:8000/demo/export
```

Or run the local helper:

```bash
./.venv/bin/python scripts/run_demo_export.py
```

## Demo Output Files

Generated files are stored in `demo_output/`:

- `demo_output/results_summary.csv`
- `demo_output/sample_predictions.json`
- `demo_output/sample_orders.json`
- `demo_output/pm_trader_stats.json`

These files are demo artifacts only. Counts, orders, PnL-like values, and performance fields are paper/simulated/demo results, not real trading results.

## Known Limitations

- Realized weather outcomes are not available yet, so accuracy, Brier score, and log loss are not computed.
- Apify returns a safe failed-source snapshot when `APIFY_API_TOKEN` is not configured.
- Market data uses deterministic mock fallback unless a read-only pm-trader source is configured and available.
- The default system uses local SQLite and deterministic data for repeatable demos.
- The model is a baseline probability model, not a profitability claim.
- Paper decisions are simulated local audit records.

## Future Improvements / Bonus Roadmap

- Add real realized-weather outcome ingestion for post-event scoring.
- Add richer calibration analysis once outcomes exist.
- Add more cities and market matching strategies.
- Improve read-only market matching quality when external data is available.
- Add model comparison experiments while preserving paper-only safety.
- Add deployment packaging for a hosted demo environment.
