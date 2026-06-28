# 13 - Submission Plan

## Purpose

This document defines the final internship-ready deliverables and how the `polymarket-paper-trader` integration should be presented.

## Current MVP Decision

Submit the project as a Hermes-powered weather-market research agent that uses `polymarket-paper-trader` for Polymarket market search, order-book context, paper execution, simulated portfolio, history, and stats.

The final project remains paper-trading only.

## Implementation Notes

### Technology Stack Additions

```txt
polymarket-paper-trader
pm-trader
PolymarketPaperTraderAdapter
```

### Setup Commands

```bash
pip install polymarket-paper-trader
pm-trader init --balance 10000
```

### README Requirements

The README should include:

```txt
Polymarket paper-trader integration
How to initialize pm-trader paper account
How market search works
How paper execution works
How portfolio/stats are displayed
How mock fallback works
Why the project is paper-trading only
```

### Assignment Mapping

```txt
Polymarket paper trading resource -> polymarket-paper-trader integration
Real Polymarket order-book paper simulation -> pm-trader price/book/buy/sell
Paper P&L/stats -> pm-trader portfolio/history/stats
Weather data requirement -> global/local/Apify weather pipeline
Agent requirement -> Hermes WeatherMarketAgent
UI requirement -> Streamlit dashboard
Risk requirement -> backend RiskService with fractional Kelly sizing
```

### Final Deliverables

```txt
Working FastAPI backend
Hermes Agent orchestration
OpenRouter configuration
Apify weather scraping configuration
polymarket-paper-trader integration
PolymarketPaperTraderAdapter
Streamlit dashboard
Risk-managed paper execution
Local DB audit mirror
Statistical evaluation outputs
README
.env.example
Demo video
Output examples
```

### Final Positioning

Suggested submission wording:

```txt
This project implements a Hermes-powered weather-market research agent that collects global and local weather data, searches Polymarket weather markets through polymarket-paper-trader, compares model probabilities with market-implied probabilities, and runs risk-managed paper execution with local audit records and statistical evaluation.

The system is designed as a research and paper-trading simulation. It does not perform non-paper execution.
```

## Acceptance Checklist

- [ ] `polymarket-paper-trader` is listed as a key integration.
- [ ] `pm-trader init --balance 10000` is documented.
- [ ] README requirements include `Polymarket paper-trader integration`.
- [ ] README requirements explain portfolio/history/stats.
- [ ] Assignment mapping references pm-trader price/book/buy/sell.
- [ ] Final positioning remains paper-trading only.

---

## Resource Usage Disclosure

- `polymarket-paper-trader` is used for paper execution and Polymarket market data.
- PolyWeather is used as architecture inspiration only.
- Apify is used as a possible weather ingestion source.
- Screenshots are used as dashboard inspiration only.
- Social media posts are used as strategy inspiration only.
- No unverified ROI/profit claims are presented as project results.
- No real-money trading is implemented.
