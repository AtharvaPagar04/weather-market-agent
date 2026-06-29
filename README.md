# Weather Market Agent

Weather Market Agent is a local, paper-trading-only research system for weather-related prediction markets. It collects deterministic weather signals for five cities, maps them to mock or read-only Polymarket-style market data, generates baseline rain probabilities, applies conservative risk checks, simulates paper decisions, and exports demo-ready evaluation artifacts.

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

## What The System Does

The backend runs a complete local pipeline for Mumbai, London, New York, Tokyo, and Sydney:

1. Refresh global/local/Apify-style weather snapshots.
2. Refresh mock or read-only Polymarket-style market snapshots.
3. Generate model probabilities.
4. Compare model probability with market-implied probability.
5. Analyze risk and Kelly-style paper sizing.
6. Record simulated paper orders or skipped paper decisions.
7. Store agent run logs.
8. Export demo-ready evaluation artifacts.

## Completed Features

- 5-city weather market pipeline
- Global/local/Apify weather source flow
- Polymarket/mock market pipeline
- Prediction model
- Risk management / Kelly-style sizing
- Paper trading simulation
- Streamlit dashboard
- Evaluation metrics
- Demo output exports
- Optional Telegram alerts, disabled by default
- Scale/deployment notes for submission review

## Architecture

Core services:

- `WeatherService`
- `MarketService`
- `PredictionService`
- `RiskService`
- `PaperTradingService`
- `AgentOrchestrationService`
- `EvaluationService`
- `AlertService`

The agent layer orchestrates existing services only. It does not bypass risk management and does not directly create paper decisions.

## Setup

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

Copy optional environment values from `.env.example` if needed. No external credentials are required for the deterministic local demo.

Telegram alerts are optional:

```txt
TELEGRAM_ALERTS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

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

```bash
BACKEND_API_URL=http://127.0.0.1:8000 ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py
```

Dashboard pages:

- Overview
- Predictions
- Risk Dashboard
- Paper Trades
- Agent Logs
- Results / Evaluation

## Run Agent Pipeline

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Export Demo Outputs

```bash
curl -X POST http://127.0.0.1:8000/demo/export
```

Final one-command smoke test:

```bash
./.venv/bin/python scripts/final_smoke_test.py
```

The smoke test validates export behavior in an isolated temporary workspace. Use `POST /demo/export` when you want to refresh the repository `demo_output/` files.

Generated files:

- `demo_output/results_summary.csv`
- `demo_output/sample_predictions.json`
- `demo_output/sample_orders.json`
- `demo_output/pm_trader_stats.json`

## Telegram Alerts

Alert endpoints:

- `GET /alerts/status`
- `POST /alerts/test`
- `POST /alerts/latest-run`

Alerts are disabled by default. If disabled or missing configuration, the API returns a safe skipped response. Alert text reports only paper/simulated/demo decisions.

## Submission Docs

- `docs/demo_runbook.md`
- `docs/submission_checklist.md`
- `docs/evaluator_architecture_summary.md`
- `docs/scale_and_deployment.md`
- `docs/final_demo_script.md`
- `docs/final_submission_package.md`
- `scripts/final_smoke_test.py`

## Known Limitations

- Realized weather outcomes are not available yet, so accuracy, Brier score, and log loss are not computed.
- Apify records a safe failed-source snapshot when `APIFY_API_TOKEN` is not configured.
- Mock market data is fallback/demo-only.
- The model is a baseline research model, not a profitability claim.
- Paper decisions are simulated local audit records.

## Future Improvements

- Add realized-weather outcome ingestion.
- Add calibration analysis after outcomes exist.
- Upgrade SQLite to Postgres for multi-user deployments.
- Add scheduled agent runs through a queue or Cron.
- Add idempotent notification tracking for optional Telegram alerts.
