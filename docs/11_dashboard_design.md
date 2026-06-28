# 11 - Dashboard Design

## Purpose

This document defines how the Streamlit dashboard displays weather signals, Polymarket market context, pm-trader paper execution, local audit data, risk decisions, and evaluation results.

## Current MVP Decision

The dashboard should show both pm-trader data and local audit data. pm-trader provides simulated portfolio/history/stats, while the local database provides the explanatory audit trail linking weather, prediction, risk, and paper execution.

## Implementation Notes

### Global Safety Warning Banner

The dashboard should show a visible warning on Overview and Paper Trades pages:

```txt
Paper trading only - all execution shown is simulated through polymarket-paper-trader. No real funds, wallets, private keys, or real-money orders are used.
```

The warning should be visible before any portfolio, order, or P&L information.

Recommended pages:

```txt
Overview
Paper Trades
Risk Dashboard
Results
```

The warning must not be hidden inside expandable details.

### Main Pages

```txt
Overview
City detail
Predictions
Paper trades
Risk dashboard
Results
```

### Paper Trades Page Sections

```txt
pm-trader Portfolio
pm-trader Trade History
pm-trader Stats
Local Audit Orders
```

### Dashboard Cards

```txt
Paper Balance
Simulated Portfolio Value
Simulated P&L
ROI
Win Rate
Max Drawdown
Open Positions
```

### Source Labels

Use clear labels in all relevant tables and cards:

```txt
Execution Source: polymarket-paper-trader
Audit Source: local database
Market Source: pm-trader order book
Fallback Market Source: mock
```

### Overview Table

The overview page should show:

```txt
City
Market slug
Market probability
Model probability
Edge
Confidence
Risk level
Recommended side
Paper execution status
Execution source
Latest decision
```

### Local Audit Orders

The local audit table should show:

```txt
paper_order_id
prediction_id
risk_report_id
market_snapshot_id
market_slug
paper_execution_source
pm_trader_order_id
status
explanation
created_at
```

### Consistency Handling

If pm-trader stats and local audit counts differ, show both values and label them clearly. Do not hide differences because they are useful for debugging and final reporting.

## Acceptance Checklist

- [ ] `pm-trader Portfolio` is documented.
- [ ] `pm-trader Trade History` is documented.
- [ ] `pm-trader Stats` is documented.
- [ ] `Execution Source: polymarket-paper-trader` is documented.
- [ ] `Audit Source: local database` is documented.
- [ ] Dashboard clearly separates pm-trader data from local DB mirror data.

---

## Terminal-Inspired MVP Dashboard Panels

The terminal/dashboard screenshots are inspiration only. The MVP dashboard should prioritize clarity over visual complexity.

Required MVP panels:

- `Market Watch`
- `Weather Evidence`
- `Probability Tracker`
- `Edge Matrix`
- `Risk Decision`
- `Paper Portfolio`
- `Transaction Feed`
- `Agent Explanation`

Fields to show where relevant:

- city
- market title
- current midpoint
- best bid
- best ask
- spread
- liquidity
- model probability
- market probability
- raw edge
- tradeable edge
- confidence interval
- source disagreement
- paper P&L
- invalidation rule

Globe map is a future enhancement, not MVP.
