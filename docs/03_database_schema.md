# 03 — Database Schema

## 1. Purpose of This Document

This document defines the database schema for the Weather-Market Research Agent.

The database is the source of truth for:

* Tracked cities
* Weather snapshots
* Market snapshots
* Generated predictions
* Risk reports
* Paper trade decisions
* Simulated positions
* Agent run logs
* Evaluation results
* Demo output data

The goal of this document is to make implementation of the SQLAlchemy models and Pydantic schemas straightforward.

---

## 2. Database Choice

The MVP will use SQLite.

SQLite is selected because:

```txt id="vy0b7j"
It is simple to run locally
It does not require external database setup
It is enough for an internship assignment MVP
It makes the project easy to clone and demo
It works well with SQLAlchemy
```

The database can later be migrated to PostgreSQL if needed.

---

## 3. Database File

Default database file:

```txt id="8q8c3b"
weather_agent.db
```

Default database URL:

```txt id="mj4cd6"
sqlite:///./weather_agent.db
```

Environment variable:

```txt id="k6kzxa"
DATABASE_URL=sqlite:///./weather_agent.db
```

---

## 4. ORM and Schema Tools

The project will use:

```txt id="w821c1"
SQLAlchemy for database models
Pydantic for API request and response schemas
SQLite for storage
```

Expected files:

```txt id="tjb3ds"
app/database.py
app/models/db_models.py
app/models/schemas.py
```

---

## 5. Main Database Tables

The MVP database will contain these tables:

```txt id="i97141"
cities
weather_snapshots
market_snapshots
predictions
risk_reports
paper_orders
positions
evaluation_results
agent_runs
agent_run_logs
```

Optional later tables:

```txt id="e04gfh"
resolved_outcomes
source_health
model_versions
```

These optional tables are not required for the first implementation unless time allows.

---

## 6. Entity Relationship Overview

```txt id="rhi904"
cities
  ├── weather_snapshots
  ├── market_snapshots
  ├── predictions
  │     └── risk_reports
  │            └── paper_orders
  │                   └── positions
  ├── evaluation_results
  └── agent_run_logs

agent_runs
  └── agent_run_logs
```

Main relationship flow:

```txt id="1o0ubn"
City
  ↓
Weather Snapshot
  ↓
Market Snapshot
  ↓
Prediction
  ↓
Risk Report
  ↓
Paper Order
  ↓
Position
  ↓
Evaluation Result
```

---

## 7. Common Column Conventions

Most tables should include:

```txt id="1tghp8"
id
created_at
updated_at
```

Datetime format:

```txt id="b86jxe"
UTC datetime should be used internally where possible.
```

SQLite storage note:

```txt id="18qoen"
SQLite does not enforce timezone-aware datetime strongly.
The application should store ISO-compatible UTC timestamps consistently.
```

Primary key convention:

```txt id="2sasml"
id INTEGER PRIMARY KEY AUTOINCREMENT
```

Foreign key convention:

```txt id="bk9u1x"
Foreign keys should reference the parent table's id column.
```

---

## 8. Table: cities

## 8.1 Purpose

The `cities` table stores the 5 active MVP cities and any future tracked cities.

Each city represents one location for which the system will collect weather data, read or mock market data, generate predictions, and simulate paper trades.

---

## 8.2 Columns

| Column       |     Type | Required | Description                                |
| ------------ | -------: | -------: | ------------------------------------------ |
| id           |  Integer |      Yes | Primary key                                |
| name         |   String |      Yes | City name                                  |
| country      |   String |      Yes | Country name                               |
| country_code |   String |       No | ISO-style country code, such as IN, US, GB |
| timezone     |   String |       No | IANA timezone, such as Asia/Kolkata        |
| latitude     |    Float |       No | City latitude                              |
| longitude    |    Float |       No | City longitude                             |
| is_active    |  Boolean |      Yes | Whether city is tracked                    |
| created_at   | DateTime |      Yes | Record creation timestamp                  |
| updated_at   | DateTime |      Yes | Last update timestamp                      |

---

## 8.3 Example Record

```json id="woq16j"
{
  "id": 1,
  "name": "Mumbai",
  "country": "India",
  "country_code": "IN",
  "timezone": "Asia/Kolkata",
  "latitude": 19.076,
  "longitude": 72.8777,
  "is_active": true,
  "created_at": "2026-06-28T10:00:00Z",
  "updated_at": "2026-06-28T10:00:00Z"
}
```

---

## 8.4 Constraints

```txt id="qy0ots"
name + country should be unique
is_active should default to true
```

Suggested unique constraint:

```txt id="wyxaj8"
UNIQUE(name, country)
```

---

## 8.5 Indexes

```txt id="l3zzr5"
index on name
index on country
index on is_active
```

---

## 9. Table: weather_snapshots

## 9.1 Purpose

The `weather_snapshots` table stores normalized weather data from all weather sources.

Each row represents one weather reading from one source for one city at one point in time.

The system should not overwrite old weather snapshots because prior predictions and evaluation need historical context.

---

## 9.2 Columns

| Column            |     Type | Required | Description                               |
| ----------------- | -------: | -------: | ----------------------------------------- |
| id                |  Integer |      Yes | Primary key                               |
| city_id           |  Integer |      Yes | Foreign key to cities.id                  |
| city_name         |   String |      Yes | Denormalized city name for easier display |
| country           |   String |      Yes | Denormalized country name                 |
| source            |   String |      Yes | global, local, apify, mock                |
| source_name       |   String |       No | Specific provider or actor name           |
| source_confidence |    Float |      Yes | Confidence score between 0 and 1          |
| observed_at       | DateTime |      Yes | Time data was observed or fetched         |
| forecast_for      | DateTime |       No | Target forecast date/time                 |
| temperature_c     |    Float |       No | Temperature in Celsius                    |
| humidity_pct      |    Float |       No | Humidity percentage                       |
| rain_probability  |    Float |       No | Rain probability between 0 and 1          |
| wind_speed_kph    |    Float |       No | Wind speed in km/h                        |
| pressure_hpa      |    Float |       No | Atmospheric pressure                      |
| cloud_cover_pct   |    Float |       No | Cloud cover percentage                    |
| precipitation_mm  |    Float |       No | Expected or observed precipitation        |
| weather_condition |   String |       No | Text condition such as cloudy/rainy       |
| raw_payload       |     Text |       No | Raw source response as JSON string        |
| status            |   String |      Yes | success, partial, failed                  |
| error_message     |     Text |       No | Error message if source failed            |
| created_at        | DateTime |      Yes | Record creation timestamp                 |

---

## 9.3 Source Enum

Allowed `source` values:

```txt id="3lxq15"
global
local
apify
mock
```

---

## 9.4 Status Enum

Allowed `status` values:

```txt id="q6cj2m"
success
partial
failed
```

---

## 9.5 Example Record

```json id="7dwc9y"
{
  "id": 1,
  "city_id": 1,
  "city_name": "Mumbai",
  "country": "India",
  "source": "apify",
  "source_name": "apify_weather_api",
  "source_confidence": 0.75,
  "observed_at": "2026-06-28T10:00:00Z",
  "forecast_for": "2026-06-29T00:00:00Z",
  "temperature_c": 30.5,
  "humidity_pct": 82,
  "rain_probability": 0.74,
  "wind_speed_kph": 12.1,
  "pressure_hpa": 1008,
  "cloud_cover_pct": 91,
  "precipitation_mm": 8.4,
  "weather_condition": "rain",
  "raw_payload": "{}",
  "status": "success",
  "error_message": null,
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 9.6 Constraints

```txt id="lg5elt"
rain_probability must be between 0 and 1
source_confidence must be between 0 and 1
humidity_pct should be between 0 and 100 when present
cloud_cover_pct should be between 0 and 100 when present
```

SQLite does not strictly enforce all validation, so these should also be validated in Pydantic/service logic.

---

## 9.7 Indexes

```txt id="owex3r"
index on city_id
index on source
index on observed_at
index on forecast_for
index on city_id + observed_at
index on city_id + source + observed_at
```

---

## 10. Table: market_snapshots

## 10.1 Purpose

The `market_snapshots` table stores prediction market data.

Each row represents one market price snapshot for one city.

For the MVP, this table supports both live and mock market snapshots.

---

## 10.2 Columns

| Column              |     Type | Required | Description                        |
| ------------------- | -------: | -------: | ---------------------------------- |
| id                  |  Integer |      Yes | Primary key                        |
| city_id             |  Integer |      Yes | Foreign key to cities.id           |
| city_name           |   String |      Yes | Denormalized city name             |
| market_id           |   String |      Yes | External or mock market identifier |
| question            |   String |      Yes | Market question                    |
| outcome_type        |   String |      Yes | rain, temperature, wind, other     |
| target_value        |    Float |       No | Threshold value, such as 25°C      |
| target_unit         |   String |       No | Unit, such as celsius or mm        |
| yes_price           |    Float |      Yes | YES price between 0 and 1          |
| no_price            |    Float |      Yes | NO price between 0 and 1           |
| implied_probability |    Float |      Yes | Market-implied YES probability     |
| volume              |    Float |       No | Market volume                      |
| liquidity           |    Float |       No | Available liquidity                |
| end_date            | DateTime |       No | Market end date                    |
| source_type         |   String |      Yes | live, mock, static                 |
| source_name         |   String |       No | Provider name                      |
| raw_payload         |     Text |       No | Raw response as JSON string        |
| fetched_at          | DateTime |      Yes | Snapshot fetch time                |
| created_at          | DateTime |      Yes | Record creation timestamp          |

---

## 10.3 Source Type Enum

Allowed `source_type` values:

```txt id="pzu3uh"
live
mock
static
```

---

## 10.4 Outcome Type Enum

Allowed `outcome_type` values:

```txt id="30tb4m"
rain
temperature
wind
humidity
other
```

---

## 10.5 Example Record

```json id="9j15pq"
{
  "id": 1,
  "city_id": 1,
  "city_name": "Mumbai",
  "market_id": "mock_mumbai_rain_001",
  "question": "Will it rain in Mumbai tomorrow?",
  "outcome_type": "rain",
  "target_value": null,
  "target_unit": null,
  "yes_price": 0.42,
  "no_price": 0.58,
  "implied_probability": 0.42,
  "volume": 12000,
  "liquidity": 5000,
  "end_date": "2026-06-29T23:59:00Z",
  "source_type": "mock",
  "source_name": "mock_market_generator",
  "raw_payload": "{}",
  "fetched_at": "2026-06-28T10:00:00Z",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 10.6 Constraints

```txt id="vl8sas"
yes_price must be between 0 and 1
no_price must be between 0 and 1
implied_probability must be between 0 and 1
volume should be >= 0
liquidity should be >= 0
```

For MVP:

```txt id="a6jps4"
implied_probability = yes_price
no_price = 1 - yes_price
```

---

## 10.7 Indexes

```txt id="iwd9c6"
index on city_id
index on market_id
index on fetched_at
index on source_type
index on city_id + fetched_at
```

---

## 11. Table: predictions

## 11.1 Purpose

The `predictions` table stores model-generated probability forecasts.

Each row represents one prediction for one city and one market snapshot.

Predictions should never overwrite previous predictions because the dashboard must show prior predictions.

---

## 11.2 Columns

| Column                   |     Type | Required | Description                           |
| ------------------------ | -------: | -------: | ------------------------------------- |
| id                       |  Integer |      Yes | Primary key                           |
| city_id                  |  Integer |      Yes | Foreign key to cities.id              |
| city_name                |   String |      Yes | Denormalized city name                |
| market_snapshot_id       |  Integer |       No | Foreign key to market_snapshots.id    |
| model_version            |   String |      Yes | Forecast model version                |
| prediction_type          |   String |      Yes | rain, temperature, wind, other        |
| model_probability        |    Float |      Yes | Model probability between 0 and 1     |
| confidence               |    Float |      Yes | Prediction confidence between 0 and 1 |
| global_signal            |    Float |       No | Signal from global weather source     |
| local_signal             |    Float |       No | Signal from local weather source      |
| apify_signal             |    Float |       No | Signal from Apify source              |
| recent_trend_signal      |    Float |       No | Recent trend signal                   |
| source_confidence_signal |    Float |       No | Combined source confidence            |
| source_agreement         |    Float |       No | Agreement score between sources       |
| reason                   |     Text |      Yes | Human-readable explanation            |
| generated_by             |   String |      Yes | baseline, hermes_agent, fallback      |
| generated_at             | DateTime |      Yes | Prediction generation time            |
| created_at               | DateTime |      Yes | Record creation timestamp             |

---

## 11.3 Prediction Type Enum

Allowed `prediction_type` values:

```txt id="ex6lam"
rain
temperature
wind
humidity
other
```

---

## 11.4 Generated By Enum

Allowed `generated_by` values:

```txt id="iem5hu"
baseline
hermes_agent
fallback
```

---

## 11.5 Example Record

```json id="0lqp85"
{
  "id": 1,
  "city_id": 1,
  "city_name": "Mumbai",
  "market_snapshot_id": 1,
  "model_version": "baseline_v1",
  "prediction_type": "rain",
  "model_probability": 0.68,
  "confidence": 0.74,
  "global_signal": 0.66,
  "local_signal": 0.72,
  "apify_signal": 0.70,
  "recent_trend_signal": 0.61,
  "source_confidence_signal": 0.78,
  "source_agreement": 0.84,
  "reason": "Global, local, and Apify weather sources all indicate elevated rain probability.",
  "generated_by": "baseline",
  "generated_at": "2026-06-28T10:00:00Z",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 11.6 Constraints

```txt id="evtmr7"
model_probability must be between 0 and 1
confidence must be between 0 and 1
source_agreement must be between 0 and 1 when present
```

---

## 11.7 Indexes

```txt id="c9up02"
index on city_id
index on market_snapshot_id
index on generated_at
index on model_version
index on city_id + generated_at
```

---

## 12. Table: risk_reports

## 12.1 Purpose

The `risk_reports` table stores the risk analysis created for each prediction.

Every prediction should receive a risk report, even if the trade is rejected.

This makes skipped trades explainable.

---

## 12.2 Columns

| Column                    |     Type | Required | Description                            |
| ------------------------- | -------: | -------: | -------------------------------------- |
| id                        |  Integer |      Yes | Primary key                            |
| city_id                   |  Integer |      Yes | Foreign key to cities.id               |
| city_name                 |   String |      Yes | Denormalized city name                 |
| prediction_id             |  Integer |      Yes | Foreign key to predictions.id          |
| market_snapshot_id        |  Integer |      Yes | Foreign key to market_snapshots.id     |
| model_probability         |    Float |      Yes | Copied from prediction                 |
| market_probability        |    Float |      Yes | Copied from market snapshot            |
| edge                      |    Float |      Yes | model_probability - market_probability |
| confidence                |    Float |      Yes | Copied from prediction                 |
| risk_level                |   String |      Yes | low, medium, high, blocked             |
| trade_allowed             |  Boolean |      Yes | Whether paper trade is allowed         |
| recommended_side          |   String |      Yes | YES, NO, NONE                          |
| recommended_size          |    Float |      Yes | Suggested paper trade size             |
| bankroll                  |    Float |      Yes | Simulated bankroll at decision time    |
| max_trade_risk_pct        |    Float |      Yes | Max allowed risk per trade             |
| max_total_exposure_pct    |    Float |      Yes | Max allowed total exposure             |
| current_total_exposure    |    Float |      Yes | Exposure before new trade              |
| kelly_fraction            |    Float |       No | Raw Kelly fraction                     |
| fractional_kelly_fraction |    Float |       No | Reduced Kelly fraction                 |
| liquidity_adjustment      |    Float |       No | Size reduction due to liquidity        |
| rejection_reason          |     Text |       No | Reason if trade is not allowed         |
| reason                    |     Text |      Yes | Human-readable explanation             |
| created_at                | DateTime |      Yes | Record creation timestamp              |

---

## 12.3 Risk Level Enum

Allowed `risk_level` values:

```txt id="2nfruo"
low
medium
high
blocked
```

---

## 12.4 Recommended Side Enum

Allowed `recommended_side` values:

```txt id="4k91py"
YES
NO
NONE
```

---

## 12.5 Example Approved Record

```json id="emx5y7"
{
  "id": 1,
  "city_id": 2,
  "city_name": "London",
  "prediction_id": 1,
  "market_snapshot_id": 1,
  "model_probability": 0.58,
  "market_probability": 0.42,
  "edge": 0.16,
  "confidence": 0.72,
  "risk_level": "medium",
  "trade_allowed": true,
  "recommended_side": "YES",
  "recommended_size": 15.0,
  "bankroll": 1000.0,
  "max_trade_risk_pct": 0.02,
  "max_total_exposure_pct": 0.10,
  "current_total_exposure": 35.0,
  "kelly_fraction": 0.12,
  "fractional_kelly_fraction": 0.03,
  "liquidity_adjustment": 1.0,
  "rejection_reason": null,
  "reason": "Positive edge with acceptable confidence and exposure.",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 12.6 Example Rejected Record

```json id="cw54fp"
{
  "id": 2,
  "city_id": 3,
  "city_name": "Tokyo",
  "prediction_id": 2,
  "market_snapshot_id": 2,
  "model_probability": 0.51,
  "market_probability": 0.49,
  "edge": 0.02,
  "confidence": 0.71,
  "risk_level": "blocked",
  "trade_allowed": false,
  "recommended_side": "NONE",
  "recommended_size": 0.0,
  "bankroll": 1000.0,
  "max_trade_risk_pct": 0.02,
  "max_total_exposure_pct": 0.10,
  "current_total_exposure": 35.0,
  "kelly_fraction": 0.0,
  "fractional_kelly_fraction": 0.0,
  "liquidity_adjustment": 0.0,
  "rejection_reason": "Edge below minimum threshold.",
  "reason": "No trade because the model edge is too small.",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 12.7 Constraints

```txt id="e8mpqp"
model_probability must be between 0 and 1
market_probability must be between 0 and 1
confidence must be between 0 and 1
recommended_size must be >= 0
bankroll must be >= 0
```

---

## 12.8 Indexes

```txt id="oogc9g"
index on city_id
index on prediction_id
index on market_snapshot_id
index on trade_allowed
index on risk_level
index on created_at
```

---

## 13. Table: paper_orders

## 13.1 Purpose

The `paper_orders` table stores simulated paper trade decisions.

This table must never represent real-money orders.

Every row is a local simulation record only.

---

## 13.2 Columns

| Column             |     Type | Required | Description                                |
| ------------------ | -------: | -------: | ------------------------------------------ |
| id                 |  Integer |      Yes | Primary key                                |
| city_id            |  Integer |      Yes | Foreign key to cities.id                   |
| city_name          |   String |      Yes | Denormalized city name                     |
| risk_report_id     |  Integer |      Yes | Foreign key to risk_reports.id             |
| prediction_id      |  Integer |      Yes | Foreign key to predictions.id              |
| market_snapshot_id |  Integer |      Yes | Foreign key to market_snapshots.id         |
| market_id          |   String |      Yes | External or mock market identifier         |
| side               |   String |      Yes | YES, NO, NONE                              |
| simulated_price    |    Float |      Yes | Paper entry price                          |
| size               |    Float |      Yes | Simulated trade size                       |
| notional_value     |    Float |      Yes | size * simulated_price or simplified stake |
| model_probability  |    Float |      Yes | Probability from prediction                |
| market_probability |    Float |      Yes | Probability from market                    |
| edge               |    Float |      Yes | Prediction edge                            |
| risk_level         |   String |      Yes | low, medium, high, blocked                 |
| status             |   String |      Yes | paper_order_created, paper_order_skipped   |
| reason             |     Text |      Yes | Human-readable order reason                |
| created_at         | DateTime |      Yes | Record creation timestamp                  |

---

## 13.3 Side Enum

Allowed `side` values:

```txt id="b1y5vh"
YES
NO
NONE
```

---

## 13.4 Status Enum

Allowed `status` values:

```txt id="m0f1hn"
paper_order_created
paper_order_skipped
```

Do not use ambiguous real-trading terms such as:

```txt id="9l0557"
order_placed
trade_executed
```

unless they are clearly prefixed with `paper_`.

---

## 13.5 Example Created Paper Order

```json id="563k62"
{
  "id": 1,
  "city_id": 2,
  "city_name": "London",
  "risk_report_id": 1,
  "prediction_id": 1,
  "market_snapshot_id": 1,
  "market_id": "mock_london_rain_001",
  "side": "YES",
  "simulated_price": 0.42,
  "size": 15.0,
  "notional_value": 15.0,
  "model_probability": 0.58,
  "market_probability": 0.42,
  "edge": 0.16,
  "risk_level": "medium",
  "status": "paper_order_created",
  "reason": "Paper YES order created due to positive edge and acceptable risk.",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 13.6 Example Skipped Paper Order

```json id="cucd33"
{
  "id": 2,
  "city_id": 3,
  "city_name": "Tokyo",
  "risk_report_id": 2,
  "prediction_id": 2,
  "market_snapshot_id": 2,
  "market_id": "mock_tokyo_rain_001",
  "side": "NONE",
  "simulated_price": 0.0,
  "size": 0.0,
  "notional_value": 0.0,
  "model_probability": 0.51,
  "market_probability": 0.49,
  "edge": 0.02,
  "risk_level": "blocked",
  "status": "paper_order_skipped",
  "reason": "Paper order skipped because edge is below minimum threshold.",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 13.7 Constraints

```txt id="i77scb"
size must be >= 0
simulated_price must be between 0 and 1 for YES/NO orders
notional_value must be >= 0
paper_order_created should have size > 0
paper_order_skipped should have size = 0
```

---

## 13.8 Indexes

```txt id="avj4ow"
index on city_id
index on market_id
index on side
index on status
index on created_at
index on prediction_id
index on risk_report_id
```

---

## 14. Table: positions

## 14.1 Purpose

The `positions` table stores current simulated paper positions.

A position represents the cumulative paper exposure for one city, market, and side.

---

## 14.2 Columns

| Column               |     Type | Required | Description                        |
| -------------------- | -------: | -------: | ---------------------------------- |
| id                   |  Integer |      Yes | Primary key                        |
| city_id              |  Integer |      Yes | Foreign key to cities.id           |
| city_name            |   String |      Yes | Denormalized city name             |
| market_id            |   String |      Yes | External or mock market identifier |
| side                 |   String |      Yes | YES or NO                          |
| total_size           |    Float |      Yes | Total simulated position size      |
| average_price        |    Float |      Yes | Average entry price                |
| current_market_price |    Float |       No | Latest market price                |
| total_cost           |    Float |      Yes | Total simulated cost               |
| unrealized_pnl       |    Float |      Yes | Estimated unrealized PnL           |
| realized_pnl         |    Float |      Yes | Realized simulated PnL             |
| status               |   String |      Yes | open, closed                       |
| opened_at            | DateTime |      Yes | First position timestamp           |
| updated_at           | DateTime |      Yes | Last position update timestamp     |

---

## 14.3 Status Enum

Allowed `status` values:

```txt id="kafrik"
open
closed
```

---

## 14.4 Example Record

```json id="33g7tx"
{
  "id": 1,
  "city_id": 2,
  "city_name": "London",
  "market_id": "mock_london_rain_001",
  "side": "YES",
  "total_size": 25.0,
  "average_price": 0.44,
  "current_market_price": 0.47,
  "total_cost": 11.0,
  "unrealized_pnl": 1.75,
  "realized_pnl": 0.0,
  "status": "open",
  "opened_at": "2026-06-28T10:00:00Z",
  "updated_at": "2026-06-28T10:30:00Z"
}
```

---

## 14.5 Constraints

```txt id="0flb54"
total_size must be >= 0
average_price must be between 0 and 1
current_market_price must be between 0 and 1 when present
total_cost must be >= 0
```

---

## 14.6 Indexes

```txt id="2lcejx"
index on city_id
index on market_id
index on side
index on status
unique index on market_id + side
```

---

## 15. Table: evaluation_results

## 15.1 Purpose

The `evaluation_results` table stores statistical metrics from saved predictions and paper trades.

This table supports the final assignment requirement for statistical results.

---

## 15.2 Columns

| Column            |     Type | Required | Description                                  |
| ----------------- | -------: | -------: | -------------------------------------------- |
| id                |  Integer |      Yes | Primary key                                  |
| evaluation_run_id |   String |      Yes | Unique evaluation run identifier             |
| metric_name       |   String |      Yes | Name of metric                               |
| metric_value      |    Float |       No | Numeric metric value                         |
| metric_text       |     Text |       No | Text result when numeric value is not enough |
| city_id           |  Integer |       No | Optional city-level metric                   |
| city_name         |   String |       No | Optional city name                           |
| sample_size       |  Integer |       No | Number of records used                       |
| notes             |     Text |       No | Explanation or limitations                   |
| created_at        | DateTime |      Yes | Record creation timestamp                    |

---

## 15.3 Metric Names

Supported metrics:

```txt id="domph9"
prediction_accuracy
brier_score
log_loss
mean_absolute_error
simulated_pnl
win_rate
max_drawdown
average_confidence
average_edge
paper_orders_created
paper_orders_skipped
```

---

## 15.4 Example Records

```json id="p8bg4i"
{
  "id": 1,
  "evaluation_run_id": "eval_20260628_100000",
  "metric_name": "brier_score",
  "metric_value": 0.182,
  "metric_text": null,
  "city_id": null,
  "city_name": null,
  "sample_size": 25,
  "notes": "Computed using simulated outcomes for MVP demo.",
  "created_at": "2026-06-28T10:00:00Z"
}
```

```json id="x1thgz"
{
  "id": 2,
  "evaluation_run_id": "eval_20260628_100000",
  "metric_name": "simulated_pnl",
  "metric_value": 17.4,
  "metric_text": null,
  "city_id": null,
  "city_name": null,
  "sample_size": 8,
  "notes": "PnL is simulated from paper orders only.",
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 15.5 Indexes

```txt id="f0i2f8"
index on evaluation_run_id
index on metric_name
index on city_id
index on created_at
```

---

## 16. Table: agent_runs

## 16.1 Purpose

The `agent_runs` table stores one row per full agent execution.

A full run may process all 5 cities.

---

## 16.2 Columns

| Column                    |     Type | Required | Description                         |
| ------------------------- | -------: | -------: | ----------------------------------- |
| id                        |  Integer |      Yes | Primary key                         |
| run_type                  |   String |      Yes | all_cities or single_city           |
| status                    |   String |      Yes | running, completed, partial, failed |
| cities_requested          |  Integer |      Yes | Number of cities requested          |
| cities_processed          |  Integer |      Yes | Number of cities completed          |
| weather_snapshots_created |  Integer |      Yes | Count of weather rows created       |
| market_snapshots_created  |  Integer |      Yes | Count of market rows created        |
| predictions_created       |  Integer |      Yes | Count of predictions created        |
| risk_reports_created      |  Integer |      Yes | Count of risk reports created       |
| paper_orders_created      |  Integer |      Yes | Count of created paper orders       |
| paper_orders_skipped      |  Integer |      Yes | Count of skipped orders             |
| started_at                | DateTime |      Yes | Start timestamp                     |
| finished_at               | DateTime |       No | Finish timestamp                    |
| summary                   |     Text |       No | JSON string or text summary         |
| error_message             |     Text |       No | Error if run failed                 |
| created_at                | DateTime |      Yes | Record creation timestamp           |

---

## 16.3 Status Enum

Allowed `status` values:

```txt id="7z8uc2"
running
completed
partial
failed
```

---

## 16.4 Run Type Enum

Allowed `run_type` values:

```txt id="gw6hjv"
all_cities
single_city
```

---

## 16.5 Example Record

```json id="s9i07p"
{
  "id": 1,
  "run_type": "all_cities",
  "status": "completed",
  "cities_requested": 5,
  "cities_processed": 5,
  "weather_snapshots_created": 15,
  "market_snapshots_created": 5,
  "predictions_created": 5,
  "risk_reports_created": 5,
  "paper_orders_created": 3,
  "paper_orders_skipped": 2,
  "started_at": "2026-06-28T10:00:00Z",
  "finished_at": "2026-06-28T10:00:20Z",
  "summary": "{}",
  "error_message": null,
  "created_at": "2026-06-28T10:00:00Z"
}
```

---

## 16.6 Indexes

```txt id="5mwlxa"
index on status
index on run_type
index on started_at
index on created_at
```

---

## 17. Table: agent_run_logs

## 17.1 Purpose

The `agent_run_logs` table stores step-level execution logs.

This table is useful for:

```txt id="0ogf99"
Debugging
Dashboard explanation
Showing what the agent did
Tracking failures and fallbacks
Demo transparency
```

---

## 17.2 Columns

| Column        |     Type | Required | Description                       |
| ------------- | -------: | -------: | --------------------------------- |
| id            |  Integer |      Yes | Primary key                       |
| agent_run_id  |  Integer |      Yes | Foreign key to agent_runs.id      |
| city_id       |  Integer |       No | Foreign key to cities.id          |
| city_name     |   String |       No | Denormalized city name            |
| step_name     |   String |      Yes | Name of workflow step             |
| status        |   String |      Yes | success, partial, failed, skipped |
| message       |     Text |      Yes | Human-readable log message        |
| fallback_used |  Boolean |      Yes | Whether fallback was used         |
| error_message |     Text |       No | Error details                     |
| metadata_json |     Text |       No | Additional JSON details           |
| created_at    | DateTime |      Yes | Record creation timestamp         |

---

## 17.3 Step Name Values

Common `step_name` values:

```txt id="7omw0u"
agent_run_started
city_processing_started
weather_global_fetch
weather_local_fetch
weather_apify_fetch
weather_normalization
weather_storage
market_fetch
market_mock_generation
market_storage
prediction_generation
risk_analysis
paper_trade_decision
position_update
explanation_generation
city_processing_completed
agent_run_completed
evaluation_run
```

---

## 17.4 Status Enum

Allowed `status` values:

```txt id="5wj5xj"
success
partial
failed
skipped
```

---

## 17.5 Example Record

```json id="6hhsij"
{
  "id": 1,
  "agent_run_id": 1,
  "city_id": 1,
  "city_name": "Mumbai",
  "step_name": "prediction_generation",
  "status": "success",
  "message": "Generated model probability 0.68 with confidence 0.74.",
  "fallback_used": false,
  "error_message": null,
  "metadata_json": "{\"model_version\":\"baseline_v1\"}",
  "created_at": "2026-06-28T10:00:10Z"
}
```

---

## 17.6 Indexes

```txt id="fcfzqs"
index on agent_run_id
index on city_id
index on step_name
index on status
index on created_at
```

---

## 18. Optional Table: resolved_outcomes

## 18.1 Purpose

The `resolved_outcomes` table can be added later to store actual or simulated outcomes for evaluation.

For MVP, outcomes can also be generated directly inside the evaluator if needed.

---

## 18.2 Columns

| Column             |     Type | Required | Description                        |
| ------------------ | -------: | -------: | ---------------------------------- |
| id                 |  Integer |      Yes | Primary key                        |
| city_id            |  Integer |      Yes | Foreign key to cities.id           |
| market_snapshot_id |  Integer |      Yes | Foreign key to market_snapshots.id |
| market_id          |   String |      Yes | Market identifier                  |
| outcome_value      |  Integer |      Yes | 1 if event happened, 0 otherwise   |
| outcome_source     |   String |      Yes | live, simulated, manual            |
| resolved_at        | DateTime |      Yes | Resolution timestamp               |
| notes              |     Text |       No | Explanation                        |
| created_at         | DateTime |      Yes | Record creation timestamp          |

---

## 18.3 Outcome Source Enum

Allowed values:

```txt id="au9zs5"
live
simulated
manual
```

---

## 19. Data Type Notes

### 19.1 JSON Storage

SQLite can store JSON-like data as text.

Fields such as:

```txt id="t4j866"
raw_payload
metadata_json
summary
```

should be stored as JSON strings.

The application should use:

```txt id="am5exa"
json.dumps() before saving
json.loads() after reading
```

---

### 19.2 Money and Size Fields

For the MVP, `Float` is acceptable.

Fields:

```txt id="ccw2wk"
size
notional_value
bankroll
recommended_size
volume
liquidity
pnl
```

can use floats.

For production financial systems, decimal types would be better, but this MVP is a paper-trading simulation.

---

### 19.3 Probability Fields

All probability fields should be floats between 0 and 1.

Examples:

```txt id="mweigg"
rain_probability
yes_price
no_price
implied_probability
model_probability
confidence
source_confidence
source_agreement
```

---

## 20. Required Relationships

SQLAlchemy relationships should support:

```txt id="pplw5r"
City.weather_snapshots
City.market_snapshots
City.predictions
City.risk_reports
City.paper_orders
City.positions
City.agent_run_logs

Prediction.risk_reports
RiskReport.paper_orders
AgentRun.logs
```

Minimal relationship map:

```txt id="w04zfw"
City 1 → many WeatherSnapshot
City 1 → many MarketSnapshot
City 1 → many Prediction
City 1 → many RiskReport
City 1 → many PaperOrder
City 1 → many Position

MarketSnapshot 1 → many Prediction
Prediction 1 → many RiskReport
RiskReport 1 → many PaperOrder
AgentRun 1 → many AgentRunLog
```

---

## 21. Pydantic Schema Plan

Pydantic schemas should be created for API responses.

Suggested schemas:

```txt id="ss1sz4"
CityCreate
CityRead

WeatherSnapshotCreate
WeatherSnapshotRead

MarketSnapshotCreate
MarketSnapshotRead

PredictionCreate
PredictionRead

RiskReportCreate
RiskReportRead

PaperOrderCreate
PaperOrderRead

PositionRead

EvaluationResultRead

AgentRunRead
AgentRunLogRead
```

For MVP, many create schemas can be internal only.

The API should mainly expose read schemas and service-trigger endpoints.

---

## 22. Seed Data

The system should support seeding 5 default cities.

Default city seed:

```json id="f1g3cs"
[
  {
    "name": "Mumbai",
    "country": "India",
    "country_code": "IN",
    "timezone": "Asia/Kolkata",
    "latitude": 19.076,
    "longitude": 72.8777
  },
  {
    "name": "London",
    "country": "United Kingdom",
    "country_code": "GB",
    "timezone": "Europe/London",
    "latitude": 51.5072,
    "longitude": -0.1276
  },
  {
    "name": "New York",
    "country": "United States",
    "country_code": "US",
    "timezone": "America/New_York",
    "latitude": 40.7128,
    "longitude": -74.006
  },
  {
    "name": "Tokyo",
    "country": "Japan",
    "country_code": "JP",
    "timezone": "Asia/Tokyo",
    "latitude": 35.6762,
    "longitude": 139.6503
  },
  {
    "name": "Sydney",
    "country": "Australia",
    "country_code": "AU",
    "timezone": "Australia/Sydney",
    "latitude": -33.8688,
    "longitude": 151.2093
  }
]
```

---

## 23. Query Patterns

The database should support these common queries efficiently:

### Latest weather by city

```txt id="c5wjmy"
Get latest weather snapshots for each active city.
```

Uses:

```txt id="3selza"
weather_snapshots.city_id
weather_snapshots.observed_at
```

---

### Latest market by city

```txt id="zp9byo"
Get latest market snapshot for each active city.
```

Uses:

```txt id="0831dg"
market_snapshots.city_id
market_snapshots.fetched_at
```

---

### Latest prediction by city

```txt id="fdn1ix"
Get latest prediction for each active city.
```

Uses:

```txt id="a62mkt"
predictions.city_id
predictions.generated_at
```

---

### Prediction history

```txt id="z205bd"
Get all predictions for one city ordered by generated_at descending.
```

Uses:

```txt id="q72uqz"
predictions.city_id
predictions.generated_at
```

---

### Current positions

```txt id="r4gjlo"
Get all open paper positions.
```

Uses:

```txt id="56xhcw"
positions.status
```

---

### Latest risk reports

```txt id="xjuh5d"
Get latest risk reports for each city.
```

Uses:

```txt id="hss1z4"
risk_reports.city_id
risk_reports.created_at
```

---

### Agent run history

```txt id="7phk8p"
Get previous agent runs and logs.
```

Uses:

```txt id="cwgk34"
agent_runs.started_at
agent_run_logs.agent_run_id
```

---

## 24. Database Initialization Flow

On backend startup:

```txt id="cvgc2x"
1. Load configuration
2. Create database engine
3. Create all tables if they do not exist
4. Open database session
5. Check if cities table is empty
6. Optionally seed default MVP cities
```

For MVP, automatic table creation is acceptable.

Later, Alembic migrations can be added.

---

## 25. Migration Strategy

MVP strategy:

```txt id="is3v2v"
Use SQLAlchemy Base.metadata.create_all()
```

Future strategy:

```txt id="0gn0v5"
Use Alembic migrations
```

Do not add Alembic in the first version unless needed.

The priority is a working local demo.

---

## 26. Data Retention Strategy

For MVP:

```txt id="uoggez"
Keep all records
Do not delete old predictions
Do not delete old weather snapshots
Do not delete old market snapshots
Do not overwrite paper orders
```

Reason:

```txt id="cpkzm5"
Prior predictions and historical decisions are required for dashboard and evaluation.
```

Optional cleanup can be added later.

---

## 27. Safety Rules in Database Design

The database should make paper trading explicit.

Important safety choices:

```txt id="hklhk7"
Use table name paper_orders, not orders
Use status paper_order_created, not order_placed
Use simulated_price, not execution_price
Use size as simulated size
Never store signing credentials
Never store funded account addresses for execution
Never store exchange execution credentials
```

This keeps the project clearly positioned as a research and simulation tool.

---

## 28. Example Full Data Chain

Example for one city:

```txt id="dtsgi7"
cities.id = 1
  ↓
weather_snapshots.city_id = 1
  ↓
market_snapshots.city_id = 1
  ↓
predictions.city_id = 1 and market_snapshot_id = 1
  ↓
risk_reports.prediction_id = 1 and market_snapshot_id = 1
  ↓
paper_orders.risk_report_id = 1
  ↓
positions.market_id = paper_orders.market_id
```

This chain makes it easy to answer:

```txt id="yol8co"
Why did the agent create this paper trade?
What weather data influenced the prediction?
What was the market probability?
What was the edge?
What risk rules were applied?
What position was created?
```

---

## 29. Acceptance Checklist

This database schema is complete when:

```txt id="et8ms7"
cities table is defined
weather_snapshots table is defined
market_snapshots table is defined
predictions table is defined
risk_reports table is defined
paper_orders table is defined
positions table is defined
evaluation_results table is defined
agent_runs table is defined
agent_run_logs table is defined
Relationships are clear
Indexes are planned
Enums are documented
Seed city data is defined
Paper trading safety boundaries are clear
Prior prediction storage is supported
Evaluation result storage is supported
```

---

## 30. Implementation Checklist

When implementing this schema:

```txt id="h1jqxc"
Create app/database.py
Create SQLAlchemy Base
Create database engine
Create SessionLocal
Create get_db dependency
Create app/models/db_models.py
Create all table models
Create app/models/schemas.py
Create Pydantic schemas
Add seed city function
Add basic database test
Verify tables are created
Verify seed cities are inserted
Verify insert/read for weather snapshot
Verify insert/read for market snapshot
Verify insert/read for prediction
```

---

## 31. Minimal Phase 2 Acceptance Test

Phase 2 is accepted when the following works:

```txt id="v820ah"
1. Backend starts
2. SQLite database file is created
3. Tables are created
4. 5 default cities are inserted
5. Weather snapshot can be inserted and read
6. Market snapshot can be inserted and read
7. Prediction can be inserted and read
8. Risk report can be inserted and read
9. Paper order can be inserted and read
10. Position can be inserted and read
```

---

## 32. 60-Second Database Explanation

The database uses SQLite with SQLAlchemy.

It stores active cities, normalized weather snapshots from global, local, and Apify sources, prediction market snapshots, generated probability predictions, risk reports, paper orders, simulated positions, evaluation metrics, and agent logs.

Every important output is stored instead of overwritten, so the dashboard can show prior predictions and the evaluator can calculate statistical results.

The schema clearly separates research and simulation from real-money trading by using paper-specific tables and fields such as `paper_orders`, `simulated_price`, and `paper_order_created`.

This makes the project easy to demo, debug, evaluate, and extend.
