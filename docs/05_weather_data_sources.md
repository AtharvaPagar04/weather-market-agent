# 04 — API Design

## 1. Purpose of This Document

This document defines the FastAPI backend API design for the Weather-Market Research Agent.

The API is responsible for connecting:

```txt
Streamlit Dashboard
  ↓
FastAPI Backend
  ↓
Services
  ↓
Hermes Agent
  ↓
Database
```

This document explains:

* API endpoint groups
* Request and response shapes
* Service responsibilities behind each endpoint
* Expected status codes
* Error response format
* Dashboard usage
* MVP acceptance criteria

The API should be simple, demo-friendly, and easy to test.

---

## 2. API Design Goals

The API should support the complete MVP flow:

```txt
1. Health check
2. City management
3. Weather refresh
4. Market refresh
5. Prediction generation
6. Agent orchestration
7. Risk analysis
8. Paper trading
9. Position tracking
10. Evaluation results
11. Agent logs
```

The most important endpoint for the demo is:

```txt
POST /agent/run
```

This endpoint should run the full pipeline for all 5 cities.

---

## 3. API Base URL

For local development:

```txt
http://localhost:8000
```

For dashboard configuration:

```txt
BACKEND_API_URL=http://localhost:8000
```

---

## 4. API Versioning Decision

For the MVP, use simple routes without versioning:

```txt
/health
/cities
/weather/latest
/agent/run
```

Optional future improvement:

```txt
/api/v1/health
/api/v1/cities
/api/v1/agent/run
```

MVP decision:

```txt
Use simple non-versioned routes first.
```

Reason:

```txt
This is a short internship assignment.
Simple routes are faster to build and easier to demo.
```

---

## 5. API Endpoint Summary

| Group        | Method | Endpoint                         | Purpose                        |
| ------------ | -----: | -------------------------------- | ------------------------------ |
| Health       |    GET | `/health`                        | Check backend status           |
| Cities       |    GET | `/cities`                        | List tracked cities            |
| Cities       |   POST | `/cities/seed`                   | Seed default MVP cities        |
| Weather      |    GET | `/weather/latest`                | Get latest weather snapshots   |
| Weather      |   POST | `/weather/refresh`               | Refresh weather data           |
| Markets      |    GET | `/markets`                       | Get latest market snapshots    |
| Markets      |   POST | `/markets/refresh`               | Refresh or mock market data    |
| Predictions  |    GET | `/predictions/latest`            | Get latest predictions         |
| Predictions  |    GET | `/predictions/history/{city_id}` | Get prediction history         |
| Predictions  |   POST | `/predictions/generate`          | Generate predictions           |
| Risk         |    GET | `/risk`                          | Get latest risk reports        |
| Risk         |   POST | `/risk/analyze`                  | Run risk analysis              |
| Paper Trades |    GET | `/paper-trades`                  | List paper orders              |
| Paper Trades |   POST | `/paper-trades/run`              | Create paper trade decisions   |
| Positions    |    GET | `/positions`                     | Get current paper positions    |
| Agent        |   POST | `/agent/run`                     | Run full Hermes Agent pipeline |
| Agent        |    GET | `/agent/runs`                    | List previous agent runs       |
| Agent        |    GET | `/agent/logs`                    | List agent logs                |
| Evaluation   |   POST | `/evaluation/run`                | Generate evaluation metrics    |
| Evaluation   |    GET | `/evaluation/results`            | Read evaluation results        |
| Demo Output  |   POST | `/demo/export`                   | Export sample output files     |

---

## 6. Common Response Format

For normal object/list responses, return direct JSON.

Example:

```json
{
  "status": "ok",
  "data": []
}
```

For MVP simplicity, list endpoints can return plain arrays:

```json
[
  {
    "id": 1,
    "name": "Mumbai",
    "country": "India"
  }
]
```

Recommended API response style:

```json
{
  "success": true,
  "message": "Weather refresh completed.",
  "data": {}
}
```

MVP decision:

```txt
Use structured response for mutation/action endpoints.
Use plain list/object responses for simple read endpoints.
```

---

## 7. Common Error Response Format

All errors should use a consistent format.

Example:

```json
{
  "success": false,
  "error": {
    "code": "WEATHER_SOURCE_FAILED",
    "message": "Failed to fetch weather data from Apify.",
    "details": {
      "city": "Mumbai",
      "source": "apify"
    }
  }
}
```

Common error fields:

| Field         | Description                 |
| ------------- | --------------------------- |
| success       | Always false for error      |
| error.code    | Machine-readable error code |
| error.message | Human-readable message      |
| error.details | Optional debugging details  |

---

## 8. Common Status Codes

| Status Code | Usage                        |
| ----------: | ---------------------------- |
|         200 | Successful read or action    |
|         201 | Resource created             |
|         400 | Invalid request              |
|         404 | Resource not found           |
|         422 | Validation error             |
|         500 | Internal server error        |
|         503 | External service unavailable |

For MVP, most action endpoints can return `200` with a structured result.

---

## 9. Health API

## 9.1 GET `/health`

### Purpose

Check whether the backend is running.

This is the first endpoint to implement.

### Service Used

```txt
No service required.
```

### Request

No request body.

### Response

```json
{
  "status": "ok",
  "app_name": "Weather Market Agent",
  "environment": "development",
  "database": "connected"
}
```

### Acceptance Check

```bash
curl http://localhost:8000/health
```

Expected:

```txt
Backend returns status ok.
```

---

## 10. Cities API

## 10.1 GET `/cities`

### Purpose

Return all tracked cities.

The dashboard uses this endpoint to display the 5 MVP cities.

### Service Used

```txt
CityService
```

### Request

No request body.

Optional query parameters:

| Parameter   |    Type | Required | Description               |
| ----------- | ------: | -------: | ------------------------- |
| active_only | Boolean |       No | Return only active cities |

Example:

```txt
GET /cities?active_only=true
```

### Response

```json
[
  {
    "id": 1,
    "name": "Mumbai",
    "country": "India",
    "country_code": "IN",
    "timezone": "Asia/Kolkata",
    "latitude": 19.076,
    "longitude": 72.8777,
    "is_active": true
  },
  {
    "id": 2,
    "name": "London",
    "country": "United Kingdom",
    "country_code": "GB",
    "timezone": "Europe/London",
    "latitude": 51.5072,
    "longitude": -0.1276,
    "is_active": true
  }
]
```

### Acceptance Check

The endpoint returns at least 5 active cities after seeding.

---

## 10.2 POST `/cities/seed`

### Purpose

Seed default MVP cities into the database.

Default cities:

```txt
Mumbai
London
New York
Tokyo
Sydney
```

### Service Used

```txt
CityService.seed_default_cities()
```

### Request

No request body required.

Optional body:

```json
{
  "reset_existing": false
}
```

### Response

```json
{
  "success": true,
  "message": "Default cities seeded successfully.",
  "data": {
    "cities_created": 5,
    "cities_existing": 0,
    "total_active_cities": 5
  }
}
```

### Acceptance Check

Calling this endpoint creates the 5 MVP cities if they do not exist.

---

## 11. Weather API

## 11.1 GET `/weather/latest`

### Purpose

Return the latest weather snapshots for all cities or one city.

The dashboard uses this endpoint to show current weather signals.

### Service Used

```txt
WeatherService.get_latest_weather()
```

### Query Parameters

| Parameter |    Type | Required | Description                |
| --------- | ------: | -------: | -------------------------- |
| city_id   | Integer |       No | Filter by city             |
| source    |  String |       No | global, local, apify, mock |
| limit     | Integer |       No | Max records                |

Example:

```txt
GET /weather/latest
GET /weather/latest?city_id=1
GET /weather/latest?city_id=1&source=apify
```

### Response

```json
[
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
    "weather_condition": "rain",
    "status": "success"
  }
]
```

### Acceptance Check

The endpoint returns latest weather records grouped by city and source.

---

## 11.2 POST `/weather/refresh`

### Purpose

Fetch and store new weather data.

This endpoint can refresh:

```txt
All active cities
One selected city
Selected weather sources
```

### Service Used

```txt
WeatherService.refresh_weather()
```

### Request Body

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "sources": ["global", "local", "apify"],
  "use_mock_on_failure": true
}
```

### Request Fields

| Field               |         Type | Required | Description                       |
| ------------------- | -----------: | -------: | --------------------------------- |
| city_ids            | List Integer |       No | Cities to refresh                 |
| sources             |  List String |       No | Weather sources to use            |
| use_mock_on_failure |      Boolean |       No | Use fallback data if source fails |

If `city_ids` is missing, refresh all active cities.

If `sources` is missing, use all configured sources.

### Response

```json
{
  "success": true,
  "message": "Weather refresh completed.",
  "data": {
    "cities_processed": 5,
    "snapshots_created": 15,
    "sources_used": ["global", "local", "apify"],
    "failed_sources": [],
    "fallback_used": false
  }
}
```

### Partial Success Response

```json
{
  "success": true,
  "message": "Weather refresh completed with partial failures.",
  "data": {
    "cities_processed": 5,
    "snapshots_created": 12,
    "sources_used": ["global", "local", "apify"],
    "failed_sources": [
      {
        "city": "Tokyo",
        "source": "local",
        "error": "Local weather source unavailable"
      }
    ],
    "fallback_used": true
  }
}
```

### Acceptance Check

The endpoint creates weather snapshots for all 5 cities.

---

## 12. Markets API

## 12.1 GET `/markets`

### Purpose

Return latest market snapshots.

The dashboard uses this endpoint to show market-implied probabilities.

### Service Used

```txt
MarketService.get_latest_markets()
```

### Query Parameters

| Parameter   |    Type | Required | Description        |
| ----------- | ------: | -------: | ------------------ |
| city_id     | Integer |       No | Filter by city     |
| source_type |  String |       No | live, mock, static |
| limit       | Integer |       No | Max records        |

Example:

```txt
GET /markets
GET /markets?city_id=1
GET /markets?source_type=mock
```

### Response

```json
[
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
    "fetched_at": "2026-06-28T10:00:00Z"
  }
]
```

### Acceptance Check

The endpoint returns one latest market snapshot per active city.

---

## 12.2 POST `/markets/refresh`

### Purpose

Refresh market data for all active cities.

This endpoint should attempt live market data first if enabled.

If live data is unavailable, it should create mock market snapshots.

### Service Used

```txt
MarketService.refresh_markets()
```

### Request Body

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "use_mock_if_live_unavailable": true,
  "force_mock": false
}
```

### Request Fields

| Field                        |         Type | Required | Description                                   |
| ---------------------------- | -----------: | -------: | --------------------------------------------- |
| city_ids                     | List Integer |       No | Cities to refresh                             |
| use_mock_if_live_unavailable |      Boolean |       No | Use mock fallback                             |
| force_mock                   |      Boolean |       No | Skip live market fetch and generate mock data |

### Response

```json
{
  "success": true,
  "message": "Market refresh completed.",
  "data": {
    "cities_processed": 5,
    "market_snapshots_created": 5,
    "live_snapshots": 0,
    "mock_snapshots": 5,
    "fallback_used": true
  }
}
```

### Acceptance Check

Every active city has a latest market snapshot.

---

## 13. Predictions API

## 13.1 GET `/predictions/latest`

### Purpose

Return latest predictions for all active cities or one city.

The dashboard uses this endpoint to show model probabilities and confidence.

### Service Used

```txt
PredictionService.get_latest_predictions()
```

### Query Parameters

| Parameter     |    Type | Required | Description             |
| ------------- | ------: | -------: | ----------------------- |
| city_id       | Integer |       No | Filter by city          |
| model_version |  String |       No | Filter by model version |
| limit         | Integer |       No | Max records             |

### Response

```json
[
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
    "generated_at": "2026-06-28T10:00:00Z"
  }
]
```

### Acceptance Check

The endpoint returns latest model probability and confidence for each city.

---

## 13.2 GET `/predictions/history/{city_id}`

### Purpose

Return prior predictions for a city.

This supports the assignment requirement to show prior predictions.

### Service Used

```txt
PredictionService.get_prediction_history(city_id)
```

### Path Parameters

| Parameter |    Type | Required | Description |
| --------- | ------: | -------: | ----------- |
| city_id   | Integer |      Yes | City ID     |

### Query Parameters

| Parameter |    Type | Required | Description       |
| --------- | ------: | -------: | ----------------- |
| limit     | Integer |       No | Number of records |
| offset    | Integer |       No | Pagination offset |

Example:

```txt
GET /predictions/history/1?limit=25
```

### Response

```json
[
  {
    "id": 10,
    "city_id": 1,
    "city_name": "Mumbai",
    "model_probability": 0.68,
    "market_probability": 0.42,
    "edge": 0.26,
    "confidence": 0.74,
    "decision": "paper_order_created",
    "generated_at": "2026-06-28T10:00:00Z"
  },
  {
    "id": 9,
    "city_id": 1,
    "city_name": "Mumbai",
    "model_probability": 0.61,
    "market_probability": 0.55,
    "edge": 0.06,
    "confidence": 0.69,
    "decision": "paper_order_created",
    "generated_at": "2026-06-28T09:00:00Z"
  }
]
```

### Acceptance Check

The endpoint returns historical prediction records without overwriting old predictions.

---

## 13.3 POST `/predictions/generate`

### Purpose

Generate predictions from latest weather and market data.

This endpoint does not create paper trades.

It only creates prediction records.

### Service Used

```txt
PredictionService.generate_predictions()
```

### Request Body

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "model_version": "baseline_v1"
}
```

### Request Fields

| Field         |         Type | Required | Description                        |
| ------------- | -----------: | -------: | ---------------------------------- |
| city_ids      | List Integer |       No | Cities to generate predictions for |
| model_version |       String |       No | Model version to use               |

If `city_ids` is missing, generate predictions for all active cities.

### Response

```json
{
  "success": true,
  "message": "Predictions generated successfully.",
  "data": {
    "cities_processed": 5,
    "predictions_created": 5,
    "model_version": "baseline_v1",
    "predictions": [
      {
        "city": "Mumbai",
        "model_probability": 0.68,
        "confidence": 0.74,
        "reason": "Local and global weather sources agree on high rainfall probability."
      }
    ]
  }
}
```

### Acceptance Check

The endpoint creates one prediction for every selected city.

---

## 14. Risk API

## 14.1 GET `/risk`

### Purpose

Return latest risk reports.

The dashboard uses this endpoint for the risk dashboard and overview page.

### Service Used

```txt
RiskService.get_latest_risk_reports()
```

### Query Parameters

| Parameter     |    Type | Required | Description                       |
| ------------- | ------: | -------: | --------------------------------- |
| city_id       | Integer |       No | Filter by city                    |
| trade_allowed | Boolean |       No | Filter by allowed/rejected trades |
| risk_level    |  String |       No | low, medium, high, blocked        |
| limit         | Integer |       No | Max records                       |

### Response

```json
[
  {
    "id": 1,
    "city_id": 1,
    "city_name": "Mumbai",
    "prediction_id": 1,
    "market_snapshot_id": 1,
    "model_probability": 0.68,
    "market_probability": 0.42,
    "edge": 0.26,
    "confidence": 0.74,
    "risk_level": "medium",
    "trade_allowed": true,
    "recommended_side": "YES",
    "recommended_size": 15.0,
    "bankroll": 1000.0,
    "current_total_exposure": 35.0,
    "reason": "Positive edge with acceptable confidence and exposure.",
    "created_at": "2026-06-28T10:00:00Z"
  }
]
```

### Acceptance Check

The endpoint shows risk level, edge, recommended side, and size.

---

## 14.2 POST `/risk/analyze`

### Purpose

Run risk analysis for latest predictions.

This endpoint does not create paper orders.

It only creates risk reports.

### Service Used

```txt
RiskService.analyze_risk()
```

### Request Body

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "bankroll": 1000.0
}
```

### Request Fields

| Field    |         Type | Required | Description                 |
| -------- | -----------: | -------: | --------------------------- |
| city_ids | List Integer |       No | Cities to analyze           |
| bankroll |        Float |       No | Simulated bankroll override |

### Response

```json
{
  "success": true,
  "message": "Risk analysis completed.",
  "data": {
    "cities_processed": 5,
    "risk_reports_created": 5,
    "trade_allowed_count": 3,
    "trade_blocked_count": 2
  }
}
```

### Acceptance Check

Each latest prediction gets a risk report.

---

## 15. Paper Trades API

## 15.1 GET `/paper-trades`

### Purpose

Return paper trade records.

The dashboard uses this endpoint to show simulated orders and skipped decisions.

### Service Used

```txt
PaperTradingService.list_paper_orders()
```

### Query Parameters

| Parameter |    Type | Required | Description                                |
| --------- | ------: | -------: | ------------------------------------------ |
| city_id   | Integer |       No | Filter by city                             |
| status    |  String |       No | paper_order_created or paper_order_skipped |
| side      |  String |       No | YES, NO, NONE                              |
| limit     | Integer |       No | Max records                                |

### Response

```json
[
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
]
```

### Acceptance Check

The endpoint returns both created and skipped paper order decisions.

---

## 15.2 POST `/paper-trades/run`

### Purpose

Create paper trade decisions from latest risk reports.

This endpoint reads risk reports and creates either:

```txt
paper_order_created
paper_order_skipped
```

It must never create non-paper trades.

### Service Used

```txt
PaperTradingService.run_paper_trading()
```

### Request Body

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "dry_run": false
}
```

### Request Fields

| Field    |         Type | Required | Description                     |
| -------- | -----------: | -------: | ------------------------------- |
| city_ids | List Integer |       No | Cities to process               |
| dry_run  |      Boolean |       No | Return decisions without saving |

### Response

```json
{
  "success": true,
  "message": "Paper trading run completed.",
  "data": {
    "cities_processed": 5,
    "paper_orders_created": 3,
    "paper_orders_skipped": 2,
    "positions_updated": 3,
    "orders": [
      {
        "city": "London",
        "side": "YES",
        "simulated_price": 0.42,
        "size": 15.0,
        "status": "paper_order_created"
      },
      {
        "city": "Tokyo",
        "side": "NONE",
        "simulated_price": 0.0,
        "size": 0.0,
        "status": "paper_order_skipped"
      }
    ]
  }
}
```

### Acceptance Check

The endpoint creates paper orders and updates simulated positions.

---

## 16. Positions API

## 16.1 GET `/positions`

### Purpose

Return current paper positions.

The dashboard uses this endpoint for portfolio/risk display.

### Service Used

```txt
PositionService.get_positions()
```

### Query Parameters

| Parameter |    Type | Required | Description    |
| --------- | ------: | -------: | -------------- |
| city_id   | Integer |       No | Filter by city |
| status    |  String |       No | open or closed |
| side      |  String |       No | YES or NO      |

### Response

```json
[
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
]
```

### Acceptance Check

The endpoint returns current simulated exposure.

---

## 17. Agent API

## 17.1 POST `/agent/run`

### Purpose

Run the full Hermes Agent pipeline.

This is the most important endpoint for the MVP.

It should run:

```txt
1. Load active cities
2. Fetch weather
3. Fetch market snapshots
4. Generate predictions
5. Analyze risk
6. Create paper trade decisions
7. Update positions
8. Store logs
9. Return summary
```

### Service Used

```txt
WeatherMarketAgent.run()
```

or:

```txt
AgentOrchestrationService.run_full_pipeline()
```

### Request Body

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "force_mock_markets": false,
  "run_evaluation_after": false
}
```

### Request Fields

| Field                |         Type | Required | Description                          |
| -------------------- | -----------: | -------: | ------------------------------------ |
| city_ids             | List Integer |       No | Cities to process                    |
| force_mock_markets   |      Boolean |       No | Use mock market data                 |
| run_evaluation_after |      Boolean |       No | Run evaluation after agent completes |

If `city_ids` is missing, process all active cities.

### Response

```json
{
  "success": true,
  "message": "Agent run completed.",
  "data": {
    "agent_run_id": 7,
    "status": "completed",
    "cities_processed": 5,
    "weather_snapshots_created": 15,
    "market_snapshots_created": 5,
    "predictions_created": 5,
    "risk_reports_created": 5,
    "paper_orders_created": 3,
    "paper_orders_skipped": 2,
    "summary": [
      {
        "city": "Mumbai",
        "decision": "paper_order_created",
        "side": "YES",
        "model_probability": 0.68,
        "market_probability": 0.42,
        "edge": 0.26,
        "confidence": 0.74,
        "risk_level": "medium",
        "reason": "Positive edge with acceptable confidence and exposure."
      },
      {
        "city": "Tokyo",
        "decision": "paper_order_skipped",
        "side": "NONE",
        "model_probability": 0.51,
        "market_probability": 0.49,
        "edge": 0.02,
        "confidence": 0.71,
        "risk_level": "blocked",
        "reason": "No trade because edge is below minimum threshold."
      }
    ]
  }
}
```

### Partial Success Response

```json
{
  "success": true,
  "message": "Agent run completed with partial failures.",
  "data": {
    "agent_run_id": 8,
    "status": "partial",
    "cities_processed": 4,
    "cities_failed": 1,
    "paper_orders_created": 2,
    "paper_orders_skipped": 2,
    "failures": [
      {
        "city": "Sydney",
        "step": "weather_refresh",
        "error": "No weather source returned usable data."
      }
    ]
  }
}
```

### Acceptance Check

One API call runs the complete pipeline for all 5 cities.

---

## 17.2 GET `/agent/runs`

### Purpose

List previous agent runs.

The dashboard can use this to show prior agent activity.

### Service Used

```txt
AgentLogService.list_agent_runs()
```

### Query Parameters

| Parameter |    Type | Required | Description                |
| --------- | ------: | -------: | -------------------------- |
| status    |  String |       No | completed, partial, failed |
| limit     | Integer |       No | Max records                |

### Response

```json
[
  {
    "id": 7,
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
    "finished_at": "2026-06-28T10:00:20Z"
  }
]
```

### Acceptance Check

The endpoint shows previous run history.

---

## 17.3 GET `/agent/logs`

### Purpose

Return detailed agent step logs.

This supports explainability and debugging.

### Service Used

```txt
AgentLogService.list_logs()
```

### Query Parameters

| Parameter    |    Type | Required | Description                       |
| ------------ | ------: | -------: | --------------------------------- |
| agent_run_id | Integer |       No | Filter by run                     |
| city_id      | Integer |       No | Filter by city                    |
| status       |  String |       No | success, partial, failed, skipped |
| step_name    |  String |       No | Filter by step                    |
| limit        | Integer |       No | Max records                       |

### Response

```json
[
  {
    "id": 1,
    "agent_run_id": 7,
    "city_id": 1,
    "city_name": "Mumbai",
    "step_name": "prediction_generation",
    "status": "success",
    "message": "Generated model probability 0.68 with confidence 0.74.",
    "fallback_used": false,
    "error_message": null,
    "created_at": "2026-06-28T10:00:10Z"
  }
]
```

### Acceptance Check

The endpoint shows what the agent did step by step.

---

## 18. Evaluation API

## 18.1 POST `/evaluation/run`

### Purpose

Generate statistical results from stored predictions and paper orders.

This supports the final deliverable requiring statistical results.

### Service Used

```txt
EvaluationService.run_evaluation()
```

### Request Body

```json
{
  "use_simulated_outcomes": true,
  "export_files": true
}
```

### Request Fields

| Field                  |    Type | Required | Description                                         |
| ---------------------- | ------: | -------: | --------------------------------------------------- |
| use_simulated_outcomes | Boolean |       No | Use simulated outcomes if real outcomes unavailable |
| export_files           | Boolean |       No | Export CSV/JSON demo files                          |

### Response

```json
{
  "success": true,
  "message": "Evaluation completed.",
  "data": {
    "evaluation_run_id": "eval_20260628_100000",
    "sample_size": 25,
    "metrics": {
      "prediction_accuracy": 0.64,
      "brier_score": 0.182,
      "log_loss": 0.61,
      "mean_absolute_error": 0.31,
      "simulated_pnl": 17.4,
      "win_rate": 0.58,
      "max_drawdown": 0.07,
      "average_confidence": 0.72,
      "average_edge": 0.11
    },
    "files_exported": [
      "demo_output/results_summary.csv",
      "demo_output/sample_predictions.json",
      "demo_output/sample_orders.json"
    ]
  }
}
```

### Acceptance Check

The endpoint stores evaluation results and optionally exports output files.

---

## 18.2 GET `/evaluation/results`

### Purpose

Read latest evaluation results.

The dashboard uses this endpoint for the Results page.

### Service Used

```txt
EvaluationService.get_results()
```

### Query Parameters

| Parameter         |    Type | Required | Description              |
| ----------------- | ------: | -------: | ------------------------ |
| evaluation_run_id |  String |       No | Filter by evaluation run |
| metric_name       |  String |       No | Filter by metric         |
| city_id           | Integer |       No | Filter by city           |
| limit             | Integer |       No | Max records              |

### Response

```json
[
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
]
```

### Acceptance Check

The endpoint returns saved metrics for dashboard and README screenshots.

---

## 19. Demo Export API

## 19.1 POST `/demo/export`

### Purpose

Export sample output files for final submission.

Expected files:

```txt
demo_output/results_summary.csv
demo_output/sample_predictions.json
demo_output/sample_orders.json
```

### Service Used

```txt
DemoExportService.export_outputs()
```

or:

```txt
EvaluationService.export_outputs()
```

### Request Body

```json
{
  "include_predictions": true,
  "include_orders": true,
  "include_results": true
}
```

### Response

```json
{
  "success": true,
  "message": "Demo output files exported.",
  "data": {
    "files": [
      "demo_output/results_summary.csv",
      "demo_output/sample_predictions.json",
      "demo_output/sample_orders.json"
    ]
  }
}
```

### Acceptance Check

The required output examples are created locally.

---

## 20. Dashboard API Usage

The Streamlit dashboard should call these endpoints.

### Overview Page

Uses:

```txt
GET /cities
GET /weather/latest
GET /markets
GET /predictions/latest
GET /risk
GET /positions
```

Main button:

```txt
POST /agent/run
```

---

### City Detail Page

Uses:

```txt
GET /cities
GET /weather/latest?city_id={city_id}
GET /markets?city_id={city_id}
GET /predictions/history/{city_id}
GET /risk?city_id={city_id}
GET /paper-trades?city_id={city_id}
```

---

### Predictions Page

Uses:

```txt
GET /predictions/latest
GET /predictions/history/{city_id}
POST /predictions/generate
```

---

### Paper Trades Page

Uses:

```txt
GET /paper-trades
GET /positions
POST /paper-trades/run
```

---

### Risk Dashboard Page

Uses:

```txt
GET /risk
GET /positions
GET /paper-trades
```

---

### Results Page

Uses:

```txt
GET /evaluation/results
POST /evaluation/run
POST /demo/export
```

---

## 21. Endpoint Implementation Order

Implement endpoints in this order:

```txt
1. GET /health
2. GET /cities
3. POST /cities/seed
4. GET /weather/latest
5. POST /weather/refresh
6. GET /markets
7. POST /markets/refresh
8. POST /predictions/generate
9. GET /predictions/latest
10. POST /risk/analyze
11. GET /risk
12. POST /paper-trades/run
13. GET /paper-trades
14. GET /positions
15. POST /agent/run
16. GET /agent/runs
17. GET /agent/logs
18. POST /evaluation/run
19. GET /evaluation/results
20. POST /demo/export
```

Reason:

```txt
Build independent services first.
Then connect them through the agent endpoint.
```

---

## 22. API Route File Mapping

Suggested files:

```txt
app/api/routes_health.py
app/api/routes_cities.py
app/api/routes_weather.py
app/api/routes_markets.py
app/api/routes_predictions.py
app/api/routes_risk.py
app/api/routes_paper_trades.py
app/api/routes_positions.py
app/api/routes_agent.py
app/api/routes_evaluation.py
app/api/routes_demo.py
```

Mapping:

| File                   | Endpoints                                                                        |
| ---------------------- | -------------------------------------------------------------------------------- |
| routes_health.py       | `/health`                                                                        |
| routes_cities.py       | `/cities`, `/cities/seed`                                                        |
| routes_weather.py      | `/weather/latest`, `/weather/refresh`                                            |
| routes_markets.py      | `/markets`, `/markets/refresh`                                                   |
| routes_predictions.py  | `/predictions/latest`, `/predictions/history/{city_id}`, `/predictions/generate` |
| routes_risk.py         | `/risk`, `/risk/analyze`                                                         |
| routes_paper_trades.py | `/paper-trades`, `/paper-trades/run`                                             |
| routes_positions.py    | `/positions`                                                                     |
| routes_agent.py        | `/agent/run`, `/agent/runs`, `/agent/logs`                                       |
| routes_evaluation.py   | `/evaluation/run`, `/evaluation/results`                                         |
| routes_demo.py         | `/demo/export`                                                                   |

---

## 23. Service Mapping

| Endpoint                             | Service                                |
| ------------------------------------ | -------------------------------------- |
| GET `/cities`                        | CityService                            |
| POST `/cities/seed`                  | CityService                            |
| GET `/weather/latest`                | WeatherService                         |
| POST `/weather/refresh`              | WeatherService                         |
| GET `/markets`                       | MarketService                          |
| POST `/markets/refresh`              | MarketService                          |
| GET `/predictions/latest`            | PredictionService                      |
| GET `/predictions/history/{city_id}` | PredictionService                      |
| POST `/predictions/generate`         | PredictionService                      |
| GET `/risk`                          | RiskService                            |
| POST `/risk/analyze`                 | RiskService                            |
| GET `/paper-trades`                  | PaperTradingService                    |
| POST `/paper-trades/run`             | PaperTradingService                    |
| GET `/positions`                     | PositionService                        |
| POST `/agent/run`                    | WeatherMarketAgent                     |
| GET `/agent/runs`                    | AgentLogService                        |
| GET `/agent/logs`                    | AgentLogService                        |
| POST `/evaluation/run`               | EvaluationService                      |
| GET `/evaluation/results`            | EvaluationService                      |
| POST `/demo/export`                  | EvaluationService or DemoExportService |

---

## 24. Pydantic Request Schemas

Suggested request schemas:

```txt
SeedCitiesRequest
WeatherRefreshRequest
MarketRefreshRequest
PredictionGenerateRequest
RiskAnalyzeRequest
PaperTradeRunRequest
AgentRunRequest
EvaluationRunRequest
DemoExportRequest
```

---

## 25. Pydantic Response Schemas

Suggested response schemas:

```txt
CityRead
WeatherSnapshotRead
MarketSnapshotRead
PredictionRead
RiskReportRead
PaperOrderRead
PositionRead
AgentRunRead
AgentRunLogRead
EvaluationResultRead
ActionResponse
ErrorResponse
```

---

## 26. Request Schema Details

### SeedCitiesRequest

```json
{
  "reset_existing": false
}
```

---

### WeatherRefreshRequest

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "sources": ["global", "local", "apify"],
  "use_mock_on_failure": true
}
```

---

### MarketRefreshRequest

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "use_mock_if_live_unavailable": true,
  "force_mock": false
}
```

---

### PredictionGenerateRequest

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "model_version": "baseline_v1"
}
```

---

### RiskAnalyzeRequest

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "bankroll": 1000.0
}
```

---

### PaperTradeRunRequest

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "dry_run": false
}
```

---

### AgentRunRequest

```json
{
  "city_ids": [1, 2, 3, 4, 5],
  "force_mock_markets": false,
  "run_evaluation_after": false
}
```

---

### EvaluationRunRequest

```json
{
  "use_simulated_outcomes": true,
  "export_files": true
}
```

---

### DemoExportRequest

```json
{
  "include_predictions": true,
  "include_orders": true,
  "include_results": true
}
```

---

## 27. Action Response Schema

For action endpoints, use this common response style.

```json
{
  "success": true,
  "message": "Action completed.",
  "data": {}
}
```

Python-style schema concept:

```txt
ActionResponse:
  success: bool
  message: str
  data: dict | list | null
```

Used by:

```txt
POST /cities/seed
POST /weather/refresh
POST /markets/refresh
POST /predictions/generate
POST /risk/analyze
POST /paper-trades/run
POST /agent/run
POST /evaluation/run
POST /demo/export
```

---

## 28. Validation Rules

The API should validate:

```txt
city_ids must exist
probabilities must be between 0 and 1
risk percentages must be between 0 and 1
bankroll must be positive
sources must be valid
side must be YES, NO, or NONE
status values must be valid
```

Invalid request example:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CITY_ID",
    "message": "One or more city IDs do not exist.",
    "details": {
      "invalid_city_ids": [999]
    }
  }
}
```

---

## 29. Safety Rules for API

The API must not expose real trading endpoints.

Do not create endpoints like:

```txt
POST /orders/place
POST /trade/execute
POST /account/connect
POST /private-key
```

Allowed endpoints must clearly use paper-trading language:

```txt
POST /paper-trades/run
GET /paper-trades
GET /positions
```

Paper trading safety response should clearly say:

```txt
paper_order_created
paper_order_skipped
```

The system must not call non-paper placement APIs.

---

## 30. Mocking Rules in API

Market data can be mocked for MVP.

API responses must identify mock data.

Fields:

```txt
source_type: mock
source_name: mock_market_generator
```

Weather fallback can also be mocked if needed.

Fields:

```txt
source: mock
source_confidence: 0.50
status: success
```

Dashboard should show this clearly.

---

## 31. Agent Endpoint Internal Flow

`POST /agent/run` should internally perform:

```txt
1. Create agent_runs row with status = running
2. Load active cities
3. For each city:
   1. Fetch weather
   2. Store weather snapshots
   3. Fetch or mock market snapshot
   4. Store market snapshot
   5. Generate prediction
   6. Store prediction
   7. Analyze risk
   8. Store risk report
   9. Create paper order or skip decision
   10. Update position if order created
   11. Store city-level logs
4. Update agent_runs row with final counts
5. Return summary
```

---

## 32. Agent Endpoint Failure Handling

If one city fails:

```txt
Log failure
Continue with remaining cities
Return status = partial
```

If all cities fail:

```txt
Return status = failed
Include error summary
```

If one source fails:

```txt
Use fallback if possible
Continue city run
Log fallback
```

---

## 33. Dashboard Refresh Behavior

After `POST /agent/run`, the dashboard should refresh:

```txt
GET /weather/latest
GET /markets
GET /predictions/latest
GET /risk
GET /paper-trades
GET /positions
```

This ensures the UI reflects the latest run.

---

## 34. API Testing Plan

Minimum API tests:

```txt
test_health_returns_ok
test_seed_cities_creates_default_cities
test_get_cities_returns_seeded_cities
test_weather_refresh_creates_snapshots
test_market_refresh_creates_snapshots_or_mock_data
test_prediction_generate_creates_predictions
test_risk_analyze_creates_risk_reports
test_paper_trade_run_creates_orders_or_skips
test_agent_run_processes_all_cities
test_evaluation_run_creates_metrics
```

---

## 35. Manual Curl Test Flow

After backend starts:

```bash
curl http://localhost:8000/health
```

Seed cities:

```bash
curl -X POST http://localhost:8000/cities/seed \
  -H "Content-Type: application/json" \
  -d '{"reset_existing": false}'
```

List cities:

```bash
curl http://localhost:8000/cities
```

Refresh weather:

```bash
curl -X POST http://localhost:8000/weather/refresh \
  -H "Content-Type: application/json" \
  -d '{"use_mock_on_failure": true}'
```

Refresh markets:

```bash
curl -X POST http://localhost:8000/markets/refresh \
  -H "Content-Type: application/json" \
  -d '{"use_mock_if_live_unavailable": true}'
```

Generate predictions:

```bash
curl -X POST http://localhost:8000/predictions/generate \
  -H "Content-Type: application/json" \
  -d '{"model_version": "baseline_v1"}'
```

Run risk analysis:

```bash
curl -X POST http://localhost:8000/risk/analyze \
  -H "Content-Type: application/json" \
  -d '{"bankroll": 1000.0}'
```

Run paper trading:

```bash
curl -X POST http://localhost:8000/paper-trades/run \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

Run full agent:

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"force_mock_markets": false, "run_evaluation_after": false}'
```

Run evaluation:

```bash
curl -X POST http://localhost:8000/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{"use_simulated_outcomes": true, "export_files": true}'
```

---

## 36. MVP API Acceptance Checklist

The API design is complete when:

```txt
GET /health works
GET /cities works
POST /cities/seed works
POST /weather/refresh stores weather snapshots
GET /weather/latest returns snapshots
POST /markets/refresh stores live or mock market snapshots
GET /markets returns market snapshots
POST /predictions/generate creates predictions
GET /predictions/latest returns predictions
GET /predictions/history/{city_id} returns prior predictions
POST /risk/analyze creates risk reports
GET /risk returns risk reports
POST /paper-trades/run creates paper orders or skip decisions
GET /paper-trades returns paper orders
GET /positions returns simulated positions
POST /agent/run runs the full pipeline
GET /agent/runs returns run history
GET /agent/logs returns step logs
POST /evaluation/run creates statistical metrics
GET /evaluation/results returns metrics
POST /demo/export exports output examples
```

---

## 37. 60-Second API Explanation

The FastAPI backend exposes endpoints for the complete weather-market research pipeline.

The dashboard can call `/cities` to load tracked cities, `/weather/latest` to show weather data, `/markets` to show market probabilities, `/predictions/latest` to show model forecasts, `/risk` to show risk decisions, `/paper-trades` to show simulated orders, and `/positions` to show paper exposure.

The main demo endpoint is `POST /agent/run`. It runs the full Hermes Agent workflow for all 5 cities: weather refresh, market refresh, prediction generation, edge calculation, risk analysis, paper trade creation, position update, and logging.

The evaluation endpoints generate statistical metrics and export output examples for the final submission.

All trading-related endpoints are paper-trading only. The API does not expose non-paper trading or funded-account functionality.

---

## Apify Weather Data Scraper

The Apify Weather Data Scraper is one weather ingestion source, not the only source.

It can collect current weather, forecasts, and historical data from supported weather websites such as:

- Weather.com
- AccuWeather
- OpenWeatherMap
- Weather Underground

Important fields:

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

Apify weather output should be normalized into the internal weather schema and compared against official/local weather sources and Open-Meteo.

Normalized schema example:

```json
{
  "source": "apify_weather_scraper",
  "city": "New York",
  "observed_at": "...",
  "temperature_c": 31.2,
  "feels_like_c": 33.1,
  "humidity_percent": 64,
  "wind_speed_kph": 12.5,
  "precipitation_probability": 0.2,
  "uv_index": 6,
  "air_quality_index": 45,
  "forecast": {},
  "historical": {},
  "raw_payload": {}
}
```

Source confidence rules:

- Prefer official settlement source where available.
- Use Apify as enrichment or fallback.
- Penalize stale data.
- Penalize disagreement between sources.
- Store raw payload for audit.
