# 12 - Evaluation Metrics

## Purpose

This document defines how the MVP evaluates prediction quality, risk behavior, paper execution, simulated portfolio performance, and final reporting outputs.

## Current MVP Decision

Evaluation uses pm-trader portfolio/history/stats as additional metric inputs and local database records for assignment-specific analysis.

## Implementation Notes

### Evaluation Inputs

```txt
pm-trader portfolio
pm-trader history
pm-trader stats
local predictions
local risk reports
local paper_orders audit table
market_snapshots
weather_snapshots
evaluation_results
```

### Metrics Source Rule

When `polymarket-paper-trader` is enabled, P&L, ROI, win rate, and max drawdown should prefer pm-trader stats because it simulates Polymarket order-book execution.

The local evaluator should still calculate assignment-specific metrics such as Brier score, log loss, average edge, confidence, and blocked trade reasons.

### Core Metrics

Prediction metrics:

```txt
Prediction accuracy
Brier score
Log loss
Mean absolute error
Calibration by probability bucket
Average confidence
```

Market and edge metrics:

```txt
Average edge
Average spread
Order-book availability rate
Number of markets found by pm-trader
Number of fallback mock markets
```

Risk metrics:

```txt
Approved paper decisions
Blocked paper decisions
Blocked reason counts
Average recommended size
Exposure by city
Exposure by market_slug
```

Paper execution metrics:

```txt
Simulated P&L
ROI
Win rate
Max drawdown
Open positions
Paper balance
Simulated portfolio value
```

### Consistency Validation

Validate that pm-trader stats and local audit order counts are consistent enough for dashboard display.

If they differ, show both and label them clearly:

```txt
pm-trader source count
local audit record count
difference
possible reason
```

### Reporting Outputs

Saved outputs should include:

```txt
demo_output/results_summary.csv
demo_output/sample_predictions.json
demo_output/sample_orders.json
demo_output/pm_trader_stats.json
```

`results_summary.csv` or an equivalent output should include:

```txt
markets_matched_pct
order_book_available_pct
fallback_mock_market_pct
```

## Acceptance Checklist

- [ ] `pm-trader portfolio` is included as an evaluation input.
- [ ] `pm-trader history` is included as an evaluation input.
- [ ] `pm-trader stats` is included as an evaluation input.
- [ ] P&L, ROI, win rate, and max drawdown prefer pm-trader stats.
- [ ] The local evaluator should still calculate prediction, edge, confidence, and blocked-reason metrics.
- [ ] Differences between pm-trader stats and local audit records are labeled clearly.

---

## Resource-Informed Evaluation Metrics

Additional metrics:

- Brier score
- calibration error
- probability bucket accuracy
- edge hit rate
- no-trade precision
- paper ROI
- paper max drawdown
- win rate
- average slippage
- spread cost
- source freshness rate
- source disagreement frequency
- explanation completeness

Do not use unverified social media profit claims as target metrics. Project success should be measured using reproducible paper-trading logs and calibration metrics.

### Data Availability Metrics

The evaluator should report how much usable data was available.

Metrics:

```txt
cities_processed
markets_matched_count
markets_matched_pct
order_book_available_count
order_book_available_pct
fallback_mock_market_count
fallback_mock_market_pct
weather_sources_available_count
weather_sources_available_pct
apify_success_count
apify_failure_count
```

Purpose:

```txt
These metrics show whether results were based on real pm-trader market data, fallback mock market data, or incomplete weather inputs.
```

Example:

```json
{
  "cities_processed": 5,
  "markets_matched_count": 4,
  "markets_matched_pct": 0.80,
  "order_book_available_count": 3,
  "order_book_available_pct": 0.60,
  "fallback_mock_market_count": 1,
  "fallback_mock_market_pct": 0.20
}
```

Dashboard should show these metrics in the Results page.
