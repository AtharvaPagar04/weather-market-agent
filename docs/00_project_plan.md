# 00 - Project Plan

## Project Name

**Weather-Market Research Agent with Risk-Managed Paper Trading**

---

## 1. Purpose of This Document

This document defines the complete project plan for the internship assignment.

The goal of this document is to lock the project scope before implementation begins. It explains:

- What the project is
- What the MVP will include
- What is intentionally excluded
- Which technologies will be used
- What deliverables must be submitted
- What success looks like at the end of the project

This document should be treated as the main planning reference for the repository. Detailed build phases and implementation sequencing are maintained separately in [14_phase_wise_implementation_plan.md](14_phase_wise_implementation_plan.md).

---

## Current MVP Decision

The MVP will be a local, demo-ready Python research system that tracks five weather markets, uses `polymarket-paper-trader` for Polymarket market search and paper execution, collects weather data, generates explainable probability forecasts, compares those forecasts with market-implied probabilities, and creates risk-managed paper trades only.

The system will use FastAPI, SQLite, SQLAlchemy, Pydantic, Hermes Agent, OpenRouter, Apify, and Streamlit.

---

## 2. Final Project Positioning

This project is not a real-money trading bot.

The final submission will be positioned as:

> A Hermes-powered weather-market research agent that collects global and local weather data, generates probability forecasts, compares them with market-implied probabilities, and runs a risk-managed paper-trading simulation with statistical evaluation.

The system focuses on research, explainability, paper trading, and statistical reporting.

It does not place real-money trades.

---

## 3. Internship Assignment Interpretation

The assignment asks for a backend Python project using an agent framework that can work with prediction markets, weather data, and paper trading.

The important requirements are:

- Use Python
- Use Hermes Agent
- Use OpenRouter as the LLM provider
- Use Apify for data scraping
- Track weather markets for at least 5 cities
- Fetch global weather data
- Fetch local or country-specific weather data
- Build a model using the weather data
- Create paper trading orders
- Use risk management such as Kelly criteria
- Provide a user interface
- Show what the system is doing
- Analyze risk
- Show prior predictions
- Include statistical results
- Submit a working code repository
- Include a video demo
- Include output examples
- Include Apify token usage/configuration

The practical interpretation for this project is:

> Build a working MVP that proves the full research-to-paper-trade pipeline end to end.

---

## 4. MVP Goal

The MVP goal is to build a backend system that can:

1. Track 5 weather-related prediction markets or mock weather markets
2. Fetch weather data from multiple sources
3. Normalize weather data into a common format
4. Generate probability predictions for each city
5. Compare model probability with market-implied probability
6. Calculate edge
7. Apply conservative risk management
8. Create paper trades only
9. Track simulated positions
10. Show all important information in a Streamlit dashboard
11. Generate statistical evaluation results

The MVP should be simple, reliable, explainable, and demonstrable.

The MVP should not become overcomplicated with real-money trading, advanced machine learning, infrastructure scaling, or Telegram integration before the core flow works.

---

## 5. Core Product Summary

The system will work like this:

```txt
City
  |
  v
Weather Data Collection
  |
  v
Weather Normalization
  |
  v
Market Data Collection or Mock Market Data
  |
  v
Prediction Model
  |
  v
Market Comparison
  |
  v
Edge Calculation
  |
  v
Risk Management
  |
  v
Paper Trade Decision
  |
  v
Position Tracking
  |
  v
Evaluation + Dashboard
```

The agent should be able to run this flow for all 5 selected cities.

---

## 6. MVP Cities

The MVP will track 5 cities.

Initial suggested cities:

```txt
Mumbai, India
London, United Kingdom
New York, United States
Tokyo, Japan
Sydney, Australia
```

These cities are selected because:

- They are globally recognizable
- They belong to different countries
- They allow testing of global and local weather sources
- They are easy to explain in a demo
- They provide enough variation in climate and weather behavior

The exact cities can be changed later if market availability requires it.

---

## 7. Main User Story

As a user, I want to run one agent workflow that:

1. Fetches current weather data for 5 cities
2. Fetches or mocks prediction market prices
3. Generates a probability forecast
4. Compares forecast probability with market probability
5. Decides whether there is a tradeable edge
6. Applies risk rules
7. Creates a paper trade
8. Stores the decision
9. Shows the result in a dashboard

---

## 8. What the System Will Build

### 8.1 Backend API

The project will include a FastAPI backend.

The backend will expose endpoints for:

```txt
Health check
Cities
Weather data
Market data
Predictions
Agent execution
Paper trades
Positions
Risk reports
Evaluation results
```

The backend will be the main application layer.

### 8.2 Database

The project will use SQLite for the MVP.

SQLite is enough because:

- This is an internship assignment
- The system is local/demo focused
- It avoids unnecessary setup complexity
- It makes the project easy to clone and run

The database will store:

```txt
cities
weather_snapshots
market_snapshots
predictions
paper_orders
positions
risk_reports
evaluation_results
agent_run_logs
```

### 8.3 Weather Data Collection

The system will collect weather data from multiple sources.

Sources:

```txt
Global weather source
Local or country-specific weather source
Apify scraper
```

Each source may return data in a different structure.

The system will normalize all weather data into a common internal schema.

Example normalized format:

```json
{
  "city": "Mumbai",
  "country": "India",
  "date": "2026-06-28",
  "temperature": 30.5,
  "humidity": 82,
  "rain_probability": 0.74,
  "wind_speed": 12.1,
  "source": "apify",
  "source_confidence": 0.8
}
```

### 8.4 Market Data Reader

The system will read prediction market data in a safe, read-only way.

For the MVP, live market data is preferred but not required.

If live market integration becomes slow or unreliable, the system will use mock market data.

Market snapshot format:

```json
{
  "market_id": "mock_mumbai_rain_001",
  "city": "Mumbai",
  "question": "Will it rain in Mumbai tomorrow?",
  "yes_price": 0.42,
  "no_price": 0.58,
  "implied_probability": 0.42,
  "volume": 12000,
  "liquidity": 5000,
  "end_date": "2026-06-29"
}
```

The project should clearly mention whether a snapshot is live or mocked.

### 8.5 Prediction Model

The first version will use a baseline weighted probability model.

The baseline model should be explainable.

Initial formula:

```txt
final_probability =
  45% global weather signal
+ 35% local weather signal
+ 10% recent trend
+ 10% source confidence
```

The prediction model should output:

```json
{
  "city": "Mumbai",
  "model_probability": 0.68,
  "confidence": 0.74,
  "reason": "Local and global weather sources agree on high rainfall probability."
}
```

Advanced ML models such as Logistic Regression or Random Forest can be added later only after the baseline system works.

### 8.6 Hermes Agent Orchestration

Hermes Agent will act as the orchestration layer.

The agent should call tools in a clear order:

```txt
1. Fetch weather data
2. Fetch market data
3. Generate prediction
4. Analyze edge
5. Analyze risk
6. Create paper trade decision
7. Save explanation
```

The agent should only create risk-approved paper-trading decisions.

The agent will coordinate tools such as:

```txt
WeatherTool
PolymarketMarketTool
ForecastTool
RiskTool
PolymarketPaperTradeTool
ExplanationTool
```

### 8.7 Risk Management

Risk management is required because the system simulates trading decisions.

The MVP will use conservative rules:

```txt
Max 2% simulated bankroll per trade
Max 10% total exposure
No trade if confidence < 60%
No trade if source disagreement is high
Reduce size if market liquidity is low
Use fractional Kelly only
```

The system should always prioritize safety and explainability over aggressive returns.

### 8.8 Paper Trading

The project will only create simulated trades.

A paper trade output should look like:

```json
{
  "city": "London",
  "side": "YES",
  "simulated_price": 0.42,
  "size": 15.0,
  "model_probability": 0.58,
  "market_probability": 0.42,
  "edge": 0.16,
  "risk_level": "medium",
  "status": "paper_order_created"
}
```

Paper trading must update simulated positions but must never interact with real funds.

### 8.9 Dashboard

The dashboard will be built using Streamlit.

The dashboard should show:

```txt
Overview
City detail
Predictions
Paper trades
Risk dashboard
Results
```

The overview page should show:

```txt
City
Market probability
Model probability
Edge
Confidence
Risk level
Paper position
Latest decision
```

The dashboard is important because the assignment asks for a user interface that explains what is happening.

### 8.10 Evaluation Results

The system must produce statistical results.

Metrics:

```txt
Prediction accuracy
Brier score
Log loss
Mean absolute error
Simulated PnL
Win rate
Max drawdown
Average confidence
Average edge
```

The final submission should include saved example outputs:

```txt
demo_output/results_summary.csv
demo_output/sample_predictions.json
demo_output/sample_orders.json
```

---

## 9. Technology Stack

### Backend

```txt
Python
FastAPI
Pydantic
SQLAlchemy
SQLite
Uvicorn
```

### Agent Layer

```txt
Hermes Agent
OpenRouter
Free OpenRouter model
```

### Data Collection

```txt
Apify
Weather APIs or weather scraping
polymarket-paper-trader market reader with fallback mock market data generator
```

### Dashboard

```txt
Streamlit
Pandas
Plotly or Altair
```

### Evaluation

```txt
Pandas
NumPy
Scikit-learn metrics where useful
```

### Development

```txt
Git
Python virtual environment
.env configuration
README documentation
```

---

## Implementation Notes

Detailed implementation phases, target repository structure, branch strategy, timeline, MVP build order, and definition of done are maintained in [14_phase_wise_implementation_plan.md](14_phase_wise_implementation_plan.md).

This project plan should stay focused on scope, positioning, product behavior, technology choices, risks, and final deliverables.

---

## 10. Out of Scope for MVP

The following are intentionally excluded from the MVP:

```txt
Non-paper trading
Non-paper execution
Funded account integration
Signing credential management
Telegram bot
Advanced reinforcement learning
Complex deep learning models
High-scale distributed scraping
Cloud deployment
User authentication
Multi-user accounts
Full production monitoring
```

These may be mentioned as future improvements, but they should not block the MVP.

---

## 11. Future Improvements

After the MVP works, the following can be added as extensions:

```txt
Additional Polymarket market filters
Telegram alert bot
Advanced ML model
Historical backtesting
Better local weather sources
Hedging logic
Portfolio-level exposure optimizer
Cloud deployment
Scheduled agent runs
More cities
More market types
```

These are not required for the first working version.

---

## 12. Risk Register

### Risk 1 - Live market data integration takes too long

Mitigation:

```txt
Use mock market data for MVP.
Clearly label mock data in dashboard and documentation.
```

### Risk 2 - Weather source APIs are inconsistent

Mitigation:

```txt
Normalize all weather source outputs.
Store source name and confidence.
Allow fallback data when a source fails.
```

### Risk 3 - Hermes Agent integration becomes difficult

Mitigation:

```txt
First build services as normal Python functions.
Then expose those services as tools to Hermes Agent.
```

### Risk 4 - Project becomes too large

Mitigation:

```txt
Follow MVP priority order.
Do not add Telegram, scaling, or advanced ML before the core pipeline works.
```

### Risk 5 - Results are weak or incomplete

Mitigation:

```txt
Use saved predictions and simulated outcomes.
Generate Brier score, log loss, PnL, win rate, and drawdown from stored records.
```

---

## 13. Final Deliverables

The final submission should include:

```txt
GitHub or GitLab repository link
Working Python backend
Hermes Agent integration
Apify integration or Apify-ready tool
OpenRouter configuration
Streamlit dashboard
Paper trading simulation
Risk management logic
Statistical results
Output examples
Demo video
README
.env.example
```

---

## 14. Final Submission Message Positioning

The final email/repository description should say:

```txt
This project implements a Hermes-powered weather-market research agent that collects global and local weather data, generates probability forecasts, compares them with market-implied probabilities, and runs a risk-managed paper-trading simulation with statistical evaluation.

The system is designed as a research and paper-trading tool, not a real-money trading bot.
```

---

## 15. Acceptance Checklist for This Document

This planning document is complete when:

```txt
The MVP scope is clear
The system is positioned correctly
The technology stack is listed
The deliverables are clear
The risk register is documented
The out-of-scope items are documented
The implementation details are referenced in a separate implementation plan
The final project can be explained in 60 seconds
```

---

## 16. 60-Second Explanation

This project is a weather-market research agent built with Python, FastAPI, Hermes Agent, OpenRouter, Apify, SQLite, and Streamlit.

It tracks 5 weather markets across different cities. For each city, it collects global and local weather data, normalizes the data, generates a probability forecast, compares that forecast with market-implied probability, calculates edge, applies conservative risk management, and creates simulated paper trades.

The system includes a dashboard that shows weather signals, predictions, market prices, risk decisions, paper positions, and evaluation metrics.

It does not trade real money. It is a research and paper-trading simulation designed to demonstrate agent orchestration, data pipelines, risk management, and measurable statistical results.

---

## Resource Usage Strategy

The MVP uses external resources in a bounded way:

- Directly use `polymarket-paper-trader` for Polymarket market data, price/order-book lookup, paper execution, portfolio, history, and stats.
- Use PolyWeather as architecture inspiration for weather-market workflows, forecast consensus, probability buckets, settlement-source awareness, and explainable evidence chains.
- Use Apify as one data source for weather scraping, alongside Open-Meteo and official/local weather sources where available.
- Use dashboard screenshots as UI inspiration for clear research panels, not as a requirement to build a complex terminal clone.
- Use detector posts as strategy inspiration only; social media profit/copytrade claims are unverified and must not become expected project results.

The project remains a paper-trading research MVP.

MVP boundary:

- minimum 5 weather cities
- multi-source weather ingestion
- probability model
- Polymarket market comparison
- paper-trading simulation
- risk management
- explainable dashboard
- no real-money trading

See [15_reference_resources_analysis.md](15_reference_resources_analysis.md) for the resource mapping and exclusions.
