# 06 - Market Data Design

## Purpose

This document defines how the MVP discovers weather-related Polymarket markets, reads prices and order-book data, and normalizes market snapshots for prediction and risk analysis.

## Current MVP Decision

Primary market data source:

```txt
polymarket-paper-trader
```

The system uses `polymarket-paper-trader` to search Polymarket markets, fetch market details, read YES/NO prices, and inspect order-book data. This provides real Polymarket price context while keeping all execution paper-only.

Mock market data is fallback-only.

## Implementation Notes

### Core Architecture Terms

Required integration terms for this market data design:

```txt
polymarket-paper-trader
PolymarketPaperTraderAdapter
PolymarketMarketTool
PolymarketPaperTradeTool
```

### Primary Market Flow

```txt
Tracked city
  |
  v
Weather market search query
  |
  v
PolymarketPaperTraderAdapter
  |
  v
polymarket-paper-trader
  |
  v
Market details + price + order book
  |
  v
Normalized market_snapshots row
```

### Fallback Market Data

Mock market data is fallback-only. It is used when:

- no matching weather market is found
- `polymarket-paper-trader` is unavailable
- market data fetch fails
- local demo requires deterministic sample data

Mock records must be clearly labeled as mock and must not be presented as Polymarket data.

### Adapter Interface

```python
class PolymarketPaperTraderAdapter:
    def search_markets(self, query: str) -> list[dict]:
        ...

    def get_market(self, slug: str) -> dict:
        ...

    def get_price(self, slug: str) -> dict:
        ...

    def get_order_book(self, slug: str, depth: int = 5) -> dict:
        ...
```

### Weather Market Search Queries

Initial search examples:

```txt
Mumbai rain
London rain
New York weather
Tokyo temperature
Sydney rain
weather rain
temperature above
```

The market matcher should prefer active markets with clear city, weather-event, outcome, and date alignment.

### Normalized Market Snapshot Fields

Required base fields:

```txt
city_id
market_id
question
outcome_type
yes_price
no_price
implied_probability
volume
liquidity
end_date
source_type
source_name
fetched_at
```

Additional pm-trader fields:

```txt
market_slug
matched_query
order_book_available
best_bid
best_ask
midpoint
spread
pm_trader_source
```

`pm_trader_source` should identify whether the data came from `polymarket-paper-trader` SDK, CLI, cache, or mock fallback.

### Price and Probability Rules

- YES price maps to market-implied YES probability.
- NO price maps to market-implied NO probability.
- If order-book data is available, midpoint and spread should be calculated from best bid and best ask.
- If order-book data is unavailable, fall back to last available price fields and mark `order_book_available = false`.

### Safety Boundary

The market data layer reads market context only. It does not perform paper buy or paper sell. Paper execution is handled later by `PolymarketPaperTraderAdapter` through the paper-trading service after risk approval.

## Acceptance Checklist

- [ ] `polymarket-paper-trader` is the primary market data source.
- [ ] `market_slug` is stored.
- [ ] `order_book_available` is stored.
- [ ] `best_bid`, `best_ask`, `midpoint`, and `spread` are stored when available.
- [ ] Mock market data is fallback-only.
- [ ] Market snapshots are normalized before prediction and risk analysis.

---

## Resource-Informed Polymarket Market Data Design

`polymarket-paper-trader` strengthens the market-data design by providing:

- `markets search`
- `markets get`
- `price`
- `book`
- midpoint
- best bid
- best ask
- spread
- liquidity
- implied probability
- order book depth
- slippage estimate

Core formulas:

```txt
market_implied_probability = midpoint
raw_edge = model_probability - market_implied_probability
tradeable_edge = raw_edge - spread_cost - uncertainty_penalty - liquidity_penalty
```

The market-implied probability should come from midpoint when order-book data is available.

The market layer is read-only until risk approves a paper action. No real order is placed. Paper execution must go through `polymarket-paper-trader`.

Mock market data remains fallback/demo-only.
