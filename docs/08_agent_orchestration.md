# 08 - Agent Orchestration

## Purpose

This document defines how Hermes Agent coordinates weather collection, Polymarket market data, prediction, risk analysis, pm-trader paper execution, audit storage, and explanation.

## Current MVP Decision

Hermes `WeatherMarketAgent` orchestrates the workflow. It calls backend tools in a strict order and must use `PolymarketPaperTraderAdapter` indirectly through dedicated tools.

The agent must not bypass risk management.

## Implementation Notes

### Core Architecture Terms

Required integration terms for agent orchestration:

```txt
polymarket-paper-trader
PolymarketPaperTraderAdapter
PolymarketMarketTool
PolymarketPaperTradeTool
```

### Tool List

```txt
WeatherTool
PolymarketMarketTool
ForecastTool
RiskTool
PolymarketPaperTradeTool
ExplanationTool
```

### Tool Responsibilities

`WeatherTool`

- Fetches global, local, and Apify weather data.
- Normalizes weather records.
- Stores weather snapshots.

`PolymarketMarketTool`

- Searches for relevant weather markets.
- Fetches market price/order-book data using `PolymarketPaperTraderAdapter`.
- Stores normalized market snapshots.
- Falls back to mock market data only when pm-trader data is unavailable.

`ForecastTool`

- ForecastTool generates model probabilities from normalized weather signals only.
- Produces confidence and explanation inputs.

Market context is used separately for:

- market-implied probability
- raw edge calculation
- tradeable edge calculation
- risk analysis
- paper execution decision

`RiskTool`

- Calculates edge.
- Applies confidence, source agreement, liquidity, exposure, and fractional Kelly checks.
- Returns `trade_allowed = true` only when paper execution is permitted.

`PolymarketPaperTradeTool`

- Creates paper buy/sell actions using `polymarket-paper-trader` only after `RiskTool` approves a trade.
- Calls `PolymarketPaperTraderAdapter` for pm-trader paper buy/sell.
- Stores a local audit record.

`ExplanationTool`

- Produces a readable explanation for dashboard and reporting.
- Labels market source, execution source, and audit source.

### Forecast vs Market Separation

The model probability must be weather-first.

`ForecastTool` should not use Polymarket price as an input to the weather probability model in the MVP. This avoids market leakage.

Correct separation:

```txt
Weather data -> ForecastTool -> model_probability
Market data -> MarketTool -> market_probability
model_probability + market_probability -> RiskTool -> edge/risk decision
```

Market data can be included in explanations, but it should not directly change the baseline weather forecast probability unless a future model version explicitly documents that behavior.

### Updated Agent Flow

```txt
1. Load active city.
2. Fetch weather data.
3. Search Polymarket weather markets using pm-trader.
4. Fetch market price/order-book.
5. Generate model probability.
6. Compare model probability with market probability.
7. Run risk analysis.
8. If approved, perform pm-trader paper buy/sell.
9. Store local audit record.
10. Generate explanation.
11. Log every step.
```

### Safety Rule

The agent must never call pm-trader paper buy/sell directly. It must only call `PolymarketPaperTradeTool` after `RiskTool` returns `trade_allowed = true`.

### Audit Logging

Every agent run should store:

```txt
city
weather snapshot ids
market_slug
market snapshot id
prediction id
risk report id
paper execution decision
pm_trader_result_json when available
local audit record id
explanation
```

## Acceptance Checklist

- [ ] `PolymarketMarketTool` is documented.
- [ ] `PolymarketPaperTradeTool` is documented.
- [ ] `PolymarketPaperTraderAdapter` is used through tools.
- [ ] pm-trader paper buy/sell happens only after risk approval.
- [ ] `RiskTool returns trade_allowed = true` is required before paper execution.
- [ ] Every step creates a local audit record or log entry.

---

## Detector-Agent Architecture

Required detector tools/agents:

- `WeatherDataTool`
- `PolymarketMarketTool`
- `PolymarketPaperTradeTool`
- `WeatherSignalDetector`
- `MarketPricingDetector`
- `SourceDisagreementDetector`
- `RiskCheckTool`
- `ExplanationTool`

The Hermes agent should produce structured JSON signals:

```json
{
  "market_slug": "...",
  "city": "...",
  "contract_question": "...",
  "model_probability": 0.68,
  "market_probability": 0.56,
  "raw_edge": 0.12,
  "confidence_interval": [0.61, 0.75],
  "risk_decision": "WATCH",
  "recommended_action": "NO_TRADE",
  "evidence": [],
  "invalidation_rules": [],
  "paper_trade_request": null
}
```

Agent constraints:

- The agent cannot bypass risk manager.
- The agent cannot execute real-money trades.
- Agent explanations must cite evidence from weather sources, market data, and risk checks.
- The LLM should extract structured JSON signals, not vibes.
