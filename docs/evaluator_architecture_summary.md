# Evaluator Architecture Summary

Weather Market Agent is a local, paper-trading-only research system. It demonstrates a complete backend and dashboard workflow for weather-related prediction-market analysis without real-money execution.

Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.

## Service Layer

- `WeatherService`: refreshes normalized global, local, and Apify-style weather snapshots.
- `MarketService`: refreshes weather-market snapshots through mock fallback/demo data and read-only market adapter boundaries.
- `PredictionService`: creates baseline rain-probability predictions from weather and market snapshots.
- `RiskService`: calculates raw edge, tradeable edge, confidence/liquidity penalties, and Kelly-style paper sizing.
- `PaperTradingService`: creates local simulated paper orders or skipped paper decisions after risk analysis.
- `AgentOrchestrationService`: runs the full service pipeline and stores agent run logs.
- `EvaluationService`: summarizes descriptive demo metrics and writes export files.

## API Groups

- `/health`: backend health status.
- `/cities`: city seed and active city listing.
- `/weather`: weather refresh and latest snapshots.
- `/markets`: market refresh and market snapshots.
- `/predictions`: prediction generation and latest predictions.
- `/risk`: risk analysis and latest risk reports.
- `/paper-trades`: paper-trading simulation and local audit decisions.
- `/positions`: simulated paper positions.
- `/agent`: full pipeline orchestration, run history, and step logs.
- `/evaluation`: descriptive evaluation summary.
- `/demo/export`: demo artifact export.

## Dashboard Pages

- Overview
- Predictions
- Risk Dashboard
- Paper Trades
- Agent Logs
- Results / Evaluation

## Data Artifacts

- SQLite database: default local persistence in `weather_agent.db`.
- `demo_output/results_summary.csv`: one-row descriptive paper/simulated/demo summary.
- `demo_output/sample_predictions.json`: model-vs-market prediction examples.
- `demo_output/sample_orders.json`: simulated paper decisions, including skipped decisions.
- `demo_output/pm_trader_stats.json`: read-only/mock/unavailable pm-trader status.

## Safety Boundary

The system has no real-money trading path. Paper decisions are local simulation/audit records. Risk analysis must run before paper simulation, and demo output should not be interpreted as live performance or real profitability.
