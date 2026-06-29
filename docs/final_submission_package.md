# Final Submission Package

## Repository

- GitHub repo URL: `<add final GitHub repository URL here>`
- Branch to submit: `develop` or final `main` after review and merge
- Current final-prep branch: `phase-13-final-smoke-demo-prep`

## Required Deliverables

- README: `README.md`
- Demo video: `<add final demo video link here>`
- Final demo script: `docs/final_demo_script.md`
- Demo runbook: `docs/demo_runbook.md`
- Submission checklist: `docs/submission_checklist.md`
- Evaluator architecture summary: `docs/evaluator_architecture_summary.md`
- Scale/deployment notes: `docs/scale_and_deployment.md`
- Final smoke test: `scripts/final_smoke_test.py`

## Demo Output Files

Generate with:

```bash
curl -X POST http://127.0.0.1:8000/demo/export
```

Expected files:

- `demo_output/results_summary.csv`
- `demo_output/sample_predictions.json`
- `demo_output/sample_orders.json`
- `demo_output/pm_trader_stats.json`

These files are demo artifacts. Any order, PnL, risk, alert, or evaluation data is paper/simulated/demo-only.

## Statistical And Evaluation Files

- Evaluation API: `GET /evaluation/summary`
- Evaluation run: `POST /evaluation/run`
- Demo export: `POST /demo/export`
- Results dashboard page: Results / Evaluation

Accuracy, Brier score, and log loss are not computed until realized weather outcomes are available.

## APIFY Token Usage

`APIFY_API_TOKEN` is optional. If it is not configured, the weather pipeline records a safe missing-token fallback for the Apify source while global/local deterministic weather data continues to support the demo.

## OpenRouter / Free Model Note

`OPENROUTER_API_KEY` and `OPENROUTER_MODEL` are optional configuration fields. The local demo and test suite do not require live LLM calls or network access. The baseline prediction model is deterministic.

## Telegram Bonus Note

Telegram alerts are optional and disabled by default:

```txt
TELEGRAM_ALERTS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Alert endpoints report paper/simulated/demo status only and do not expose token values.

## Paper-Only Safety Statement

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

The repository should not include wallet connection logic, private key handling, signing credentials, funded-account logic, or live execution routes.

## Final Test Results

Record final validation results here before submission:

- Full tests: `<paste result>`
- Docs validator: `<paste result>`
- Docs tests: `<paste result>`
- Final smoke test: `<paste result>`
- Safety grep: `<paste result>`
- Manual dashboard check: `<paste result>`

## Commands To Reproduce

Install:

```bash
./.venv/bin/python -m pip install -r requirements.txt
```

Run tests:

```bash
./.venv/bin/python -m pytest tests/*.py
./.venv/bin/python scripts/validate_docs_consistency.py
./.venv/bin/python -m pytest tests/test_docs_consistency.py
```

Run final smoke test:

```bash
./.venv/bin/python scripts/final_smoke_test.py
```

Run backend:

```bash
./.venv/bin/python -m uvicorn app.main:app --reload
```

Run dashboard:

```bash
BACKEND_API_URL=http://127.0.0.1:8000 ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py
```

Run the full agent pipeline:

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Export demo outputs:

```bash
curl -X POST http://127.0.0.1:8000/demo/export
```
