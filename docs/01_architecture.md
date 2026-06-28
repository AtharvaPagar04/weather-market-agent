# 01 - Architecture

## Purpose

This document defines the current MVP architecture for the Weather-Market Research Agent after adopting `polymarket-paper-trader` as the primary Polymarket market-data and paper execution layer.

## Current MVP Decision

The project keeps ownership of the weather pipeline, prediction logic, risk engine, FastAPI backend, Hermes Agent orchestration, Streamlit dashboard, local database audit trail, and final evaluation.

`polymarket-paper-trader` owns or integrates the Polymarket-specific layer: market search, price/order-book access, paper buy, paper sell, simulated portfolio tracking, trade history, and paper-trading stats such as ROI, simulated P&L, win rate, and max drawdown.

The project remains paper-trading only.

## Implementation Notes

### Core Architecture Terms

Required integration terms for this architecture:

```txt
polymarket-paper-trader
PolymarketPaperTraderAdapter
PolymarketMarketTool
PolymarketPaperTradeTool
```

### Ownership Split

Our system owns:

```txt
weather data pipeline
Apify/global/local weather collection
weather normalization
prediction model
edge calculation
risk management
Hermes Agent orchestration
FastAPI backend
Streamlit dashboard
local database audit trail
final evaluation/reporting
```

`polymarket-paper-trader` owns or integrates:

```txt
Polymarket market search
real Polymarket price/order-book access
paper buy/sell simulation
simulated portfolio tracking
trade history
stats such as ROI, P&L, win rate, max drawdown
optional backtesting/benchmarking
```

### Core Component

`PolymarketPaperTraderAdapter`

The `PolymarketPaperTraderAdapter` is a backend integration wrapper around the `polymarket-paper-trader` package. It provides structured Python-facing methods for market search, price/order-book retrieval, paper buy/sell execution, portfolio retrieval, trade history, and stats. The adapter keeps third-party CLI/SDK details isolated from the rest of the backend.

Suggested file:

```txt
app/integrations/
  polymarket_paper_trader_client.py
```

### Market Source Strategy

Primary market path:

```txt
polymarket-paper-trader market search and order-book data
```

Fallback market path:

```txt
mock market generator, clearly labeled as mock
```

Mock market data is fallback-only and should be used only when no suitable Polymarket weather market is found, `pm-trader` is unavailable, market data fetch fails, or a deterministic local demo is required.

### Updated Architecture Flow

```txt
FastAPI / Streamlit
  |
  v
Hermes WeatherMarketAgent
  |
  v
WeatherService
  |
  v
MarketService
  |
  v
PolymarketPaperTraderAdapter
  |
  v
polymarket-paper-trader
  |
  v
PredictionService
  |
  v
RiskService
  |
  v
PaperTradingService
  |
  v
Local DB audit mirror
```

Detailed agent execution flow:

```txt
WeatherMarketAgent
  |
  v
WeatherTool
  |
  v
PolymarketMarketTool / MarketTool
  |
  v
PredictionService
  |
  v
RiskService
  |
  v
PolymarketPaperTraderAdapter
  |
  v
polymarket-paper-trader paper execution
  |
  v
Local DB audit mirror + Streamlit dashboard
```

### Safety Boundary

- The system is paper-trading only.
- No private key config should exist.
- No wallet config should exist.
- No real order endpoint should exist.
- All buy/sell wording must be written as paper buy, paper sell, pm-trader paper buy, or pm-trader paper sell.
- The local database stores a local audit record and local DB mirror for dashboard, explanations, and evaluation.

## Acceptance Checklist

- [ ] `PolymarketPaperTraderAdapter` is the only backend boundary to `polymarket-paper-trader`.
- [ ] Market search and order-book data use `polymarket-paper-trader` first.
- [ ] Mock market data is fallback-only.
- [ ] Paper execution goes through the adapter.
- [ ] Local DB audit mirror stores dashboard and reporting records.
- [ ] The architecture remains paper-trading only.

---

## Resource-Informed Detector Architecture

The latest architecture uses a detector-based design inspired by PolyWeather and detector-strategy references, with `polymarket-paper-trader` as the primary Polymarket market-data and paper-execution layer.

Required architecture modules:

- `WeatherSourceCollector`
- `WeatherNormalizer`
- `ForecastConsensusEngine`
- `ProbabilityBucketEngine`
- `PolymarketPaperTraderAdapter`
- `MarketPricingDetector`
- `WeatherSignalDetector`
- `SourceDisagreementDetector`
- `EdgeDetectionEngine`
- `RiskManager`
- `PaperExecutionService`
- `LocalAuditMirror`
- `AgentExplanationService`
- `DashboardAPI`

Resource-informed flow:

```txt
Weather sources
  |
  v
normalization
  |
  v
forecast consensus
  |
  v
probability buckets
  |
  v
Polymarket market price/order book
  |
  v
edge detection
  |
  v
risk management
  |
  v
paper execution
  |
  v
audit mirror
  |
  v
dashboard/explanation
```

Architecture clarifications:

- `polymarket-paper-trader` is the primary market-data and paper-execution layer.
- Mock market data is fallback/demo-only.
- Risk decisions remain owned by our backend, not by the paper-trader library.
- The Hermes agent produces recommendations and paper actions only.
- PolyWeather is reference-only and should not be treated as copied implementation.
