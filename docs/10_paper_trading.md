# 10 - Paper Trading

## Purpose

This document defines how the MVP creates paper buy/sell actions through `polymarket-paper-trader` and mirrors the results locally for audit, dashboard, and evaluation.

## Current MVP Decision

The paper-trading service uses `polymarket-paper-trader` as the primary paper execution engine. The backend still stores local `paper_orders` and positions as an audit mirror for dashboard, explanation, and evaluation.

The project remains paper-trading only.

## Implementation Notes

### Core Architecture Terms

Required integration terms for paper trading:

```txt
polymarket-paper-trader
PolymarketPaperTraderAdapter
PolymarketMarketTool
PolymarketPaperTradeTool
```

### Primary Component

`PolymarketPaperTraderAdapter`

Responsibilities:

```txt
Initialize paper account
Search markets
Fetch price
Fetch order book
Submit paper buy/sell
Read portfolio
Read history
Read stats
Export trades/positions if available
```

### Setup Commands

```bash
pip install polymarket-paper-trader
pm-trader init --balance 10000
```

### Adapter Interface

```python
class PolymarketPaperTraderAdapter:
    def init_account(self, balance: float = 10000.0) -> dict:
        ...

    def paper_buy(self, market_slug: str, outcome: str, amount: float) -> dict:
        ...

    def paper_sell(self, market_slug: str, outcome: str, shares: float) -> dict:
        ...

    def get_portfolio(self) -> dict:
        ...

    def get_history(self, limit: int = 50) -> list[dict]:
        ...

    def get_stats(self) -> dict:
        ...
```

### Paper Order Flow

```txt
1. Load risk report.
2. Validate trade_allowed = true.
3. Map recommended_side to pm-trader outcome.
4. Map recommended_size to paper amount.
5. Call pm-trader paper buy/sell through adapter.
6. Parse result.
7. Store local paper_order audit record.
8. Refresh portfolio/history/stats.
9. Update local position mirror if needed.
```

If risk rejects the trade, do not call pm-trader. Store `paper_order_skipped` locally.

### Local Database Meaning

The `paper_orders` table is not the execution source of truth when pm-trader is enabled. It is the project audit mirror that links `prediction_id`, `risk_report_id`, `market_snapshot_id`, `pm_trader_result`, explanation, and dashboard fields.

The local DB mirror exists so the dashboard and final evaluation can explain decisions even if pm-trader history is unavailable during review.

### Paper Order Schema Additions

Add fields:

```txt
market_slug
pm_trader_account
pm_trader_order_id
pm_trader_result_json
paper_execution_source
audit_sync_status
audit_sync_error
```

Suggested values:

```txt
paper_execution_source = polymarket-paper-trader
status = paper_order_created
status = paper_order_skipped
```

### pm-trader and Local Audit Sync Handling

When pm-trader paper execution succeeds, the backend must store a local audit record.

Possible failure:

```txt
pm-trader paper buy/sell succeeds
local database audit insert fails
```

Required behavior:

```txt
1. Log the sync failure.
2. Preserve the pm-trader response in memory for the API response when possible.
3. Return a warning that paper execution succeeded but local audit persistence failed.
4. Do not retry paper execution automatically.
5. Retry only the local audit persistence if a retry mechanism exists.
6. Dashboard should show an audit sync warning if such a record is detected.
```

Important rule:

```txt
Never submit the same pm-trader paper buy/sell twice just because local audit persistence failed.
```

Recommended field:

```txt
audit_sync_status
```

Allowed values:

```txt
synced
audit_failed
pending_reconcile
```

### Safety Rules

- Paper execution requires an approved risk report.
- The system must not call pm-trader paper buy/sell for skipped or blocked trades.
- All dashboard and API labels must say paper or simulated.
- Local audit records must preserve the original pm-trader response in `pm_trader_result_json`.

## Acceptance Checklist

- [ ] `polymarket-paper-trader as the primary paper execution engine` is documented.
- [ ] `local paper_orders and positions as an audit mirror` is documented.
- [ ] `pm-trader init --balance 10000` is documented.
- [ ] `paper_execution_source` is included.
- [ ] `pm_trader_result_json` is included.
- [ ] If risk rejects the trade, do not call pm-trader.

---

## Resource-Informed Paper Execution Audit

`polymarket-paper-trader` is the paper execution layer.

Setup:

```bash
pm-trader init --balance 10000
```

Use `pm-trader buy` and `pm-trader sell` only for paper execution through `PolymarketPaperTraderAdapter`.

The local DB audit mirror must store request, response, model probability, market probability, edge, risk decision, and paper execution result.

Required audit fields:

```txt
market_slug
outcome
side
requested_amount
model_probability
market_probability
raw_edge
tradeable_edge
risk_decision
paper_execution_source
pm_trader_result_json
created_at
```

Safety reconfirmation:

- No signing credential.
- No funded-account configuration.
- No real-money order.
- No wallet/private-key config.
