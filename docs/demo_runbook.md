# Demo Runbook

This runbook is a step-by-step script for recording the final Weather Market Agent demo video.

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

## 1. Clean Repo Check

From the repository root:

```bash
cd ~/weather-market-agent
git branch --show-current
git status --short
```

Confirm you are on the submission branch and note any intentional uncommitted demo files.

## 2. Install Requirements

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

## 3. Start Backend

Terminal 1:

```bash
./.venv/bin/python -m uvicorn app.main:app --reload
```

Quick health check:

```bash
curl http://127.0.0.1:8000/health
```

## 4. Start Dashboard

Terminal 2:

```bash
BACKEND_API_URL=http://127.0.0.1:8000 ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py
```

Open the Streamlit URL shown in the terminal.

## 5. Run Agent Pipeline

Use either the dashboard sidebar button or this API call:

```bash
curl -X POST http://127.0.0.1:8000/agent/run -H "Content-Type: application/json" -d '{}'
```

Show the response:

- `cities_processed`
- `weather_snapshots_created`
- `market_snapshots_created`
- `predictions_created`
- `risk_reports_created`
- `paper_orders_created`
- `paper_orders_skipped`

If the status is `partial`, explain that Apify can record a failed source when no token is configured while global/local deterministic weather still completes.

## 6. Show 5-City Outputs

Use API or dashboard views:

```bash
curl http://127.0.0.1:8000/cities
curl http://127.0.0.1:8000/weather/latest
curl http://127.0.0.1:8000/markets
curl http://127.0.0.1:8000/predictions/latest
curl http://127.0.0.1:8000/risk
curl http://127.0.0.1:8000/paper-trades
```

Narration points:

- The demo tracks Mumbai, London, New York, Tokyo, and Sydney.
- Weather uses global/local sources plus an Apify fallback/status path.
- Market data is mock fallback/demo data unless read-only pm-trader is available.
- Predictions compare weather probability with market probability.
- Risk gates must run before any paper decision.
- Paper decisions are simulated audit records.

## 7. Show Dashboard Pages

In Streamlit, visit:

1. Overview
2. Predictions
3. Risk Dashboard
4. Paper Trades
5. Agent Logs
6. Results / Evaluation

For each page, briefly explain the key panel:

- Overview: pipeline status and city coverage.
- Predictions: model probability, market probability, and edge.
- Risk Dashboard: risk decision, confidence, and recommended paper size.
- Paper Trades: simulated created/skipped decisions.
- Agent Logs: ordered service orchestration logs.
- Results / Evaluation: descriptive metrics and export controls.

## 8. Export Demo Output

Run:

```bash
curl -X POST http://127.0.0.1:8000/demo/export
```

Or use the Results / Evaluation page button.

## 9. Show Demo Output Files

```bash
cat demo_output/results_summary.csv
cat demo_output/sample_predictions.json
cat demo_output/sample_orders.json
cat demo_output/pm_trader_stats.json
```

Explain:

- `results_summary.csv` contains paper/simulated/demo summary counts.
- `sample_predictions.json` contains model-vs-market prediction examples.
- `sample_orders.json` contains simulated paper decisions, including skipped WATCH decisions when applicable.
- `pm_trader_stats.json` reports read-only/mock/unavailable state and confirms order execution is disabled.

## 10. Explain Fallbacks

Apify missing-token fallback:

- If `APIFY_API_TOKEN` is not configured, the Apify tool stores a failed-source snapshot instead of crashing.
- Global and local weather sources still create deterministic snapshots.
- This keeps the demo network-free and reproducible.

Mock market fallback:

- Mock market data is fallback/demo-only.
- It is used when read-only external market lookup is disabled or unavailable.
- It keeps tests and the demo deterministic.

Paper-only safety:

- No real funds are used.
- No signing credential or funded-account configuration should exist in the MVP.
- Paper decisions must pass through risk analysis and paper simulation services.
- The demo does not claim real profitability.

## 11. Suggested Demo Close

End by showing:

- `/agent/runs`
- `/agent/logs`
- `demo_output/results_summary.csv`

State clearly: this is a local paper-trading research system with deterministic demo outputs and no real-money execution.
