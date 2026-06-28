# 09 - Risk Management

## Purpose

This document defines how the project decides whether a model-market edge is strong enough for paper execution through `polymarket-paper-trader`.

## Current MVP Decision

Risk management remains owned by this backend. `polymarket-paper-trader` provides market data, paper execution, simulated portfolio, history, and stats, but it does not replace the project risk engine.

## Implementation Notes

### Risk Ownership with polymarket-paper-trader

`polymarket-paper-trader` provides market prices, order-book context, paper execution, portfolio, history, and stats. It does not replace the project risk engine.

The project `RiskService` remains responsible for:

- edge calculation
- confidence threshold
- source agreement threshold
- liquidity adjustment
- exposure limits
- fractional Kelly sizing
- blocked trade decisions

### Conservative MVP Rules

```txt
Max 2% simulated bankroll per paper trade
Max 10% total simulated exposure
No paper execution if confidence < 60%
No paper execution if source disagreement is high
Reduce size if market liquidity is weak
Use fractional Kelly only
Block any decision without a market_slug
```

### Liquidity Adjustment

If order-book data is available from `polymarket-paper-trader`, liquidity adjustment should use order-book depth, spread, and available ask/bid levels.

If order-book data is unavailable, fallback to stored liquidity field.

Liquidity inputs:

```txt
order-book depth
spread
best_bid
best_ask
available ask/bid levels
stored liquidity field
```

### Validation Before Paper Execution

Before calling `PolymarketPaperTradeTool`:

- `trade_allowed` must be true
- `recommended_side` must be YES or NO
- `recommended_size` must be greater than zero
- `market_slug` must exist
- simulated/paper execution must be enabled

If any validation fails, the system stores a blocked risk report and does not call pm-trader paper buy/sell.

### Risk Report Output

Each risk report should include:

```txt
prediction_id
market_snapshot_id
market_slug
model_probability
market_probability
raw_edge
tradeable_edge
spread_cost
uncertainty_penalty
liquidity_penalty
confidence
liquidity_score
recommended_side
recommended_size
trade_allowed
blocked_reason
risk_decision
risk_level
```

### Tradeable Edge Formula

The system should calculate both raw edge and tradeable edge.

Raw edge:

```txt
raw_edge = model_probability - market_probability
```

Tradeable edge:

```txt
tradeable_edge = raw_edge - spread_cost - uncertainty_penalty - liquidity_penalty
```

Where:

```txt
spread_cost = estimated cost from best_bid/best_ask spread
uncertainty_penalty = penalty from wide confidence interval or weak source agreement
liquidity_penalty = penalty from shallow order-book depth or low liquidity
```

Decision rule:

```txt
If tradeable_edge <= 0:
  risk_decision = NO_TRADE or WATCH

If tradeable_edge > 0 but confidence/liquidity is weak:
  risk_decision = WATCH or PAPER_TRADE_SMALL

If tradeable_edge is positive with good confidence and liquidity:
  risk_decision = PAPER_TRADE_SMALL or PAPER_TRADE_NORMAL
```

RiskService should prefer tradeable_edge for final paper execution decisions.

## Acceptance Checklist

- [ ] `Risk Ownership with polymarket-paper-trader` is documented.
- [ ] Order-book depth is used when available.
- [ ] Spread is considered in liquidity adjustment.
- [ ] `market_slug must exist` before paper execution.
- [ ] `trade_allowed must be true` before paper execution.
- [ ] Risk rejection never calls pm-trader paper buy/sell.

---

## Resource-Informed Risk Gates

Even in paper trading, risk rules must apply.

Additional MVP risk controls:

- confidence-adjusted Kelly sizing
- maximum position cap
- maximum daily loss cap
- minimum liquidity threshold
- maximum spread threshold
- uncertainty penalty
- stale-data no-trade rule
- source-disagreement no-trade rule
- manual review required state

Required decision labels:

```txt
NO_TRADE
WATCH
PAPER_TRADE_SMALL
PAPER_TRADE_NORMAL
MANUAL_REVIEW
```

Kelly output must be capped. Negative or uncertain edge should produce `NO_TRADE` or `WATCH`, not a paper action.

Risk decision examples:

- `NO_TRADE`: negative edge, stale data, very wide confidence interval, or failed validation.
- `WATCH`: positive raw edge but uncertainty or spread is too high.
- `PAPER_TRADE_SMALL`: positive tradeable_edge with conservative size.
- `PAPER_TRADE_NORMAL`: positive tradeable_edge with good confidence and liquidity.
- `MANUAL_REVIEW`: settlement-source ambiguity, unusual market wording, or conflicting evidence.
