# Reference Resources Analysis

## Directly Used Resources

`polymarket-paper-trader` is directly used as the Polymarket market-data and paper execution integration resource.

The MVP documentation assumes this resource provides:

- `pm-trader init --balance 10000`
- market search/list/get
- price lookup
- order book lookup
- paper buy/sell
- portfolio
- history
- stats
- backtesting/benchmarking
- simulated execution using real Polymarket order books
- slippage, spread, fees, and execution audit fields

The backend should wrap this dependency through `PolymarketPaperTraderAdapter` so the rest of the project works with structured Python data and local audit records.

## Architecture Reference Resources

`PolyWeather` and `PolyWeather Pro` are reference-only resources. They are used as architecture inspiration for weather-market workflows, not as copied implementation or copied code.

Useful concepts:

- weather intelligence for temperature settlement markets
- monitored cities
- multi-source weather aggregation
- forecast consensus
- probability buckets
- market bucket mapping
- model probability minus market-implied probability as edge
- settlement-source awareness
- observation-driven updates
- explainable evidence chain
- invalidation rules
- confidence and probability calibration
- dashboard/terminal workflow

The MVP should adapt these ideas into a simpler local FastAPI, Hermes Agent, SQLite, and Streamlit research system.

## Weather Data Source Resources

The Apify Weather Data Scraper is one weather ingestion source, not the only source.

It may be used to collect:

- location
- temperature
- feels-like temperature
- humidity
- wind speed
- precipitation
- UV index
- air quality
- forecast
- historical weather

Supported sites to consider:

- Weather.com
- AccuWeather
- OpenWeatherMap
- Weather Underground

Apify weather data should be compared against Open-Meteo, official settlement sources where available, and local/country-specific weather sources. It should be normalized into the internal weather schema and stored with raw payloads for audit.

## Dashboard Inspiration

Terminal/dashboard screenshots are inspiration only. They suggest useful panels, but the MVP dashboard should stay simple and readable.

Useful dashboard ideas:

- equity curve
- open positions
- market analysis
- probability tracker
- edge matrix
- transaction feed
- confidence indicator
- Bayesian/signal panel
- weather evidence panel
- risk and paper P&L panel

The MVP Streamlit dashboard should prioritize clarity over visual complexity.

## Detector Strategy Inspiration

Social media detector posts are strategy inspiration only. Social media profit/copytrade claims are unverified and must not be used as expected performance claims.

The important strategy lesson is that the system should model the market contract, not only the real-world weather event.

Bad framing:

```txt
Will the city temperature cross X?
```

Better framing:

```txt
Is the Polymarket contract mispriced compared to our model probability?
```

Detector layers to document and evaluate:

- weather detector
- market-price detector
- source-disagreement detector
- news/text detector
- risk detector

The LLM should extract structured JSON signals, not vibes. Confidence intervals and no-trade rules should protect the system from weak or uncertain signals.

## MVP Boundary

The MVP remains a paper-trading research system.

MVP boundary:

- minimum 5 weather cities
- multi-source weather ingestion
- probability model
- Polymarket market comparison
- paper-trading simulation
- risk management
- explainable dashboard
- local audit records
- no real-money trading

No signing credential or funded-account configuration should exist in the MVP.

## What We Will Not Build in MVP

The following are explicitly excluded:

- no real-money trading
- no copytrading
- no private keys
- no wallet secrets
- no signing credentials
- no funded-account configuration
- no global globe-map system in MVP
- no satellites/flights/vessels/conflict tracking in MVP
- no sports CV pipeline in MVP
- no unverified social media ROI or profit claims as target metrics

These exclusions keep the project focused on weather-market research, paper execution, risk controls, and reproducible evaluation.

## Documentation Impact

The docs should consistently reflect:

- `polymarket-paper-trader` as the direct paper execution and Polymarket market-data resource
- `PolyWeather` as reference-only architecture inspiration
- Apify Weather Data Scraper as one weather ingestion source
- terminal/dashboard screenshots as simple dashboard inspiration
- detector posts as strategy inspiration only
- mock market data as fallback/demo-only
- risk-gated paper actions only
- local DB audit mirror for reporting and evaluation

