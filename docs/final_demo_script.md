# Final Demo Script

This script is designed for a 5-8 minute project walkthrough video.

## 1. Opening

Say:

"This is Weather Market Agent, a paper-trading-only research pipeline for weather-related prediction markets. It takes weather signals for five cities, maps them to market-style data, generates model probabilities, applies risk controls, records simulated paper decisions, and exports demo evaluation files."

Safety statement:

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

## 2. Architecture Walkthrough

Show the README and explain the service pipeline:

1. `WeatherService` collects global, local, and Apify-style weather snapshots.
2. `MarketService` loads mock or read-only Polymarket-style market snapshots.
3. `PredictionService` generates baseline rain probabilities.
4. `RiskService` calculates raw edge, tradeable edge, conservative gates, and Kelly-style paper sizing.
5. `PaperTradingService` records simulated paper orders or skipped paper decisions.
6. `AgentOrchestrationService` runs the services in order and stores agent logs.
7. `EvaluationService` summarizes demo/evaluation data and writes output files.

Emphasize that the agent orchestrates existing backend services. It does not bypass risk management and does not directly create paper decisions.

## 3. Backend Startup

Run:

```bash
./.venv/bin/python -m uvicorn app.main:app --reload
```

In another terminal, verify:

```bash
curl http://127.0.0.1:8000/health
```

Expected: a healthy backend response.

## 4. Dashboard Startup

Run:

```bash
BACKEND_API_URL=http://127.0.0.1:8000 ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py
```

Open the Streamlit URL and point out the safety banner before running the pipeline.

## 5. Agent Run

Run from terminal or the dashboard:

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Explain that a `partial` status can be acceptable when Apify or optional external integrations are not configured. Global/local weather and mock/read-only fallback market data keep the demo deterministic.

## 6. Dashboard Pages

Overview page:

- Show city count and high-level pipeline status.
- Mention the five demo cities: Mumbai, London, New York, Tokyo, and Sydney.

Predictions page:

- Show model probability, market probability, raw edge, and confidence.
- Clarify these are baseline research predictions, not profitability claims.

Risk Dashboard:

- Show risk decisions such as `WATCH`, `NO_TRADE`, or paper-trade labels.
- Explain that risk approval is required before any simulated paper decision is created.

Paper Trades:

- Show simulated paper orders and skipped paper decisions.
- Clarify skipped decisions are still useful audit records.

Agent Logs:

- Show the step-by-step run logs for cities, weather, markets, predictions, risk, and paper simulation.

Results / Evaluation:

- Show counts for predictions, risk reports, weather snapshots, market snapshots, and paper decisions.
- Explain that realized weather outcomes are not available yet, so accuracy, Brier score, and log loss are not computed.

## 7. Telegram Alerts API

Show that Telegram alerts are optional and disabled by default:

```bash
curl http://127.0.0.1:8000/alerts/status

curl -X POST http://127.0.0.1:8000/alerts/test \
  -H "Content-Type: application/json" \
  -d '{}'
```

Explain that alerts only report paper/simulated/demo decisions and never include secrets.

## 8. Demo Output Files

Run:

```bash
curl -X POST http://127.0.0.1:8000/demo/export
```

Show:

- `demo_output/results_summary.csv`
- `demo_output/sample_predictions.json`
- `demo_output/sample_orders.json`
- `demo_output/pm_trader_stats.json`

Explain that the files are submission artifacts and all paper order or performance wording is simulated/demo-only.

## 9. Final Smoke Test

Optionally run the final one-command check:

```bash
./.venv/bin/python scripts/final_smoke_test.py
```

Expected final line:

```txt
FINAL SMOKE TEST PASSED
```

## 10. Known Limitations

- Apify requires an optional token; without it, the system records a safe missing-token fallback.
- Market data uses mock/read-only fallback for deterministic local testing.
- Realized weather outcomes are not ingested yet.
- Accuracy, Brier score, log loss, and real profitability analysis require future resolved-outcome backtesting.
- The current database is SQLite for local demo use.

## 11. Closing

Say:

"This submission demonstrates the full research pipeline from weather data to market snapshots, predictions, risk analysis, simulated paper decisions, dashboard visualization, evaluation summaries, exports, and optional alerts. It is intentionally paper-only and does not use real funds, wallet access, private keys, signing credentials, or live execution."
