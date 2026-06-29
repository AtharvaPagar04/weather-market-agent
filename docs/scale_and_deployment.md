# Scale And Deployment Notes

This document describes how the local Weather Market Agent demo can be scaled or deployed while preserving the project safety boundary.

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

## Current Local Demo Architecture

The current project runs as a local FastAPI backend plus Streamlit dashboard:

- FastAPI serves pipeline APIs, evaluation APIs, demo export APIs, and optional alert APIs.
- Streamlit reads from the backend through `BACKEND_API_URL`.
- SQLite stores local pipeline state in `weather_agent.db`.
- Deterministic mock/fallback sources make the demo repeatable without network access.
- Telegram alerts are optional and disabled by default.

## Backend Deployment

The backend can be deployed as a Python web service running:

```bash
./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Recommended deployment configuration:

- Set environment variables from `.env.example`.
- Keep `TELEGRAM_ALERTS_ENABLED=false` unless a demo notification channel is intentionally configured.
- Do not store secrets in source control.
- Use process-level logs for request and pipeline visibility.

## Dashboard Deployment

The dashboard can run as a separate Streamlit process:

```bash
BACKEND_API_URL=https://your-backend.example.com ./.venv/bin/python -m streamlit run dashboard/streamlit_app.py
```

The dashboard should remain read-only for analysis and paper/simulated controls.

## SQLite Limitation

SQLite is appropriate for local demos, but it is not the recommended persistence layer for concurrent production use.

Limitations:

- Single-file local storage.
- Limited concurrent write behavior.
- Harder backup and migration operations.

Recommended production upgrade:

- Move to Postgres.
- Add migrations before schema changes.
- Store generated demo artifacts in object storage if multiple instances are used.

## Background Jobs And Scheduling

For scheduled agent runs:

- Use a background job queue such as RQ, Celery, Dramatiq, or a managed queue.
- Keep `AgentOrchestrationService` as the single orchestration entrypoint.
- Do not bypass `RiskService`.
- Let `PaperTradingService` remain the only paper decision writer.

For simple periodic runs:

- Use Cron, GitHub Actions, or a managed scheduler.
- Trigger `POST /agent/run` on a safe interval.
- Trigger `POST /demo/export` after a successful or partial agent run.

## Apify Token Usage

`APIFY_API_TOKEN` is optional. If it is not configured, the Apify weather path records a safe failed-source snapshot and the global/local weather sources continue.

Do not commit token values. Use deployment environment variables.

## OpenRouter / Free Model Usage

The deterministic local demo does not require OpenRouter. If OpenRouter is used for future explanatory text, keep it optional and use free/low-cost models only when explicitly configured.

No model output should authorize non-paper execution.

## Telegram Alerts

Telegram alerts are optional:

```txt
TELEGRAM_ALERTS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Behavior:

- Disabled by default.
- Missing token or chat ID returns a skipped alert result, not a crash.
- Alert messages report only paper/simulated/demo decisions.
- Token values are never returned by status APIs.

## Observability And Logging

Recommended observability:

- API access logs.
- Agent run records in `agent_runs`.
- Step logs in `agent_run_logs`.
- Export summary files in `demo_output/`.
- Structured alert responses for skipped/sent/dry-run status.

## Horizontal Scaling Notes

If multiple backend instances are used:

- Replace SQLite with Postgres.
- Make agent runs idempotent where possible.
- Use a job queue lock to avoid duplicate scheduled runs.
- Store exports in shared storage.
- Keep alert sends idempotent by tracking run IDs.

## Rate Limits And Retry Strategy

Suggested strategy:

- Retry read-only weather/market calls with small bounded retries.
- Do not retry paper decision creation blindly; check existing `risk_report_id` decisions first.
- Back off external calls if rate-limited.
- Keep Telegram alerts best-effort and non-blocking for the pipeline.

## Data Retention Plan

Recommended MVP retention:

- Keep recent weather and market snapshots for demo traceability.
- Keep predictions, risk reports, paper decisions, positions, agent runs, and agent logs for auditability.
- Rotate old snapshots if the database grows beyond demo needs.
- Preserve final `demo_output/` files used in the submission.

## Safety Model

- No wallet configuration.
- No signing credential.
- No funded-account configuration should exist in the MVP.
- No real-money orders.
- Paper trading only.
- Telegram alerts report simulated/demo status only.
