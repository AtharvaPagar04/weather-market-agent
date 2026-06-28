# 04 - API Design

## Purpose

This document defines the planned FastAPI surface for weather-market research, Polymarket market discovery, paper execution, simulated portfolio review, and dashboard support.

## Current MVP Decision

FastAPI will expose structured JSON endpoints. Polymarket-specific market and paper-trading behavior will go through `PolymarketPaperTraderAdapter`, which wraps `polymarket-paper-trader`.

The adapter may call the package SDK or CLI internally, but the FastAPI layer should always return structured JSON.

## Implementation Notes

### Core Architecture Terms

Required integration terms for this API design:

```txt
polymarket-paper-trader
PolymarketPaperTraderAdapter
PolymarketMarketTool
PolymarketPaperTradeTool
```

### Core Endpoint Groups

```txt
GET /health
GET /cities
POST /weather/refresh
GET /weather/latest
POST /markets/refresh
GET /markets
POST /predictions/generate
GET /predictions/latest
POST /agent/run
GET /agent/logs
POST /paper-trades/run
GET /paper-trades
GET /positions
GET /risk
GET /metrics
GET /examples
```

### Polymarket Market Endpoints

```txt
GET /markets/search?query=
GET /markets/{slug}
GET /markets/{slug}/price
GET /markets/{slug}/book
```

Expected behavior:

- `GET /markets/search?query=` searches Polymarket markets through `PolymarketPaperTraderAdapter`.
- `GET /markets/{slug}` returns structured market details.
- `GET /markets/{slug}/price` returns YES/NO price context.
- `GET /markets/{slug}/book` returns order-book data when available.

### Paper Trading Endpoints

```txt
GET /paper-trades/portfolio
GET /paper-trades/history
GET /paper-trades/stats
```

Expected behavior:

- `GET /paper-trades/portfolio` returns the pm-trader simulated portfolio.
- `GET /paper-trades/history` returns pm-trader paper buy/sell history.
- `GET /paper-trades/stats` returns pm-trader stats such as ROI, simulated P&L, win rate, and max drawdown.

### Updated `POST /markets/refresh`

Behavior:

1. Search weather-related Polymarket markets through `polymarket-paper-trader`.
2. Match markets to tracked cities.
3. Pull price/order-book data.
4. Store normalized market snapshot.
5. Fall back to mock market data only if no suitable market is found or `pm-trader` is unavailable.

### Updated `POST /paper-trades/run`

Behavior:

1. Load latest risk report.
2. If risk approves, call `PolymarketPaperTraderAdapter` for pm-trader paper buy/sell.
3. Store local paper order audit record.
4. Refresh simulated portfolio/history/stats if available.

### Response Rules

- Every endpoint returns structured JSON.
- Every market response includes source labeling: `polymarket-paper-trader` or mock fallback.
- Every paper execution response includes `paper_execution_source`.
- The API does not expose endpoints for non-paper execution.

## Acceptance Checklist

- [ ] `GET /markets/search` is documented.
- [ ] `GET /markets/{slug}/book` is documented.
- [ ] `GET /paper-trades/portfolio` is documented.
- [ ] `GET /paper-trades/history` is documented.
- [ ] `GET /paper-trades/stats` is documented.
- [ ] `PolymarketPaperTraderAdapter` is documented as the API integration boundary.
- [ ] All API responses are structured JSON.
