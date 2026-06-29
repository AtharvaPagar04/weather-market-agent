# Submission Checklist

Use this checklist before recording and submitting the final project.

## Repository

- [ ] GitHub repo link is ready.
- [ ] README is updated.
- [ ] Demo runbook exists at `docs/demo_runbook.md`.
- [ ] Evaluator architecture summary exists at `docs/evaluator_architecture_summary.md`.
- [ ] Submission checklist exists at `docs/submission_checklist.md`.

## Local Runtime

- [ ] Backend runs with `./.venv/bin/python -m uvicorn app.main:app --reload`.
- [ ] Dashboard runs with `BACKEND_API_URL=http://127.0.0.1:8000 ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py`.
- [ ] `/health` returns OK.
- [ ] `/agent/run` completes or partially completes without crashing.
- [ ] Results / Evaluation dashboard page opens.

## Validation

- [ ] `./.venv/bin/python -m pytest tests/*.py` passes.
- [ ] `./.venv/bin/python scripts/validate_docs_consistency.py` passes.
- [ ] `./.venv/bin/python -m pytest tests/test_docs_consistency.py` passes.
- [ ] Safety grep shows no real execution implementation.
- [ ] No wallet, no private key, and no funded-account code is present.
- [ ] No real order execution route is present.

## Demo Outputs

- [ ] `curl -X POST http://127.0.0.1:8000/demo/export` succeeds.
- [ ] `demo_output/results_summary.csv` exists.
- [ ] `demo_output/sample_predictions.json` exists.
- [ ] `demo_output/sample_orders.json` exists.
- [ ] `demo_output/pm_trader_stats.json` exists.
- [ ] Output examples are included in the final demo or submission notes.
- [ ] Statistical results are included as descriptive paper/simulated/demo metrics only.

## Explanation Points

- [ ] Paper-trading-only safety is stated clearly.
- [ ] Apify token usage is explained. If no token is configured, explain the failed-source fallback.
- [ ] OpenRouter/free model usage is explained if applicable. The deterministic local demo does not require an OpenRouter key.
- [ ] Mock market fallback is explained as fallback/demo-only.
- [ ] No real-profitability claim is made.
- [ ] Accuracy, Brier score, and log loss are not claimed until realized weather outcomes exist.

## Video Recording Plan

- [ ] Start backend.
- [ ] Start dashboard.
- [ ] Run agent pipeline.
- [ ] Show five cities.
- [ ] Show Overview.
- [ ] Show Predictions.
- [ ] Show Risk Dashboard.
- [ ] Show Paper Trades.
- [ ] Show Agent Logs.
- [ ] Show Results / Evaluation.
- [ ] Export demo data.
- [ ] Show generated output files.
