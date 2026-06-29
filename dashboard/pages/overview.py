import streamlit as st
import pandas as pd
from dashboard.components import render_safety_banner, dataframe_from_records

def render(client):
    st.title("Overview")
    render_safety_banner()

    cities = client.get_cities()
    predictions = client.get_predictions_latest()
    risk_reports = client.get_risk()
    paper_trades = client.get_paper_trades()
    positions = client.get_positions()
    markets = client.get_markets()

    if not cities:
        st.info("No data yet. Run the agent pipeline from the sidebar.")
        return

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Cities", len(cities))
    col2.metric("Predictions", len(predictions))
    col3.metric("Risk Reports", len(risk_reports))
    col4.metric("Paper Orders", len(paper_trades))
    
    open_positions = [p for p in positions if p.get("status") == "open" and p.get("total_size", 0) > 0]
    col5.metric("Open Positions", len(open_positions))

    st.subheader("Latest System State")

    # Build joined view
    data = []
    
    # lookup dicts
    pred_map = {p["city_id"]: p for p in predictions}
    risk_map = {r["city_id"]: r for r in risk_reports}
    # paper trades could be multiple per city, get latest
    trade_map = {}
    for t in sorted(paper_trades, key=lambda x: x.get("id", 0)):
        trade_map[t["city_id"]] = t
    pos_map = {}
    for p in positions:
        pos_map[p["city_id"]] = p
    
    market_source_map = {m["city_id"]: m.get("source", "unknown") for m in markets}

    for city in cities:
        cid = city["id"]
        pred = pred_map.get(cid, {})
        risk = risk_map.get(cid, {})
        trade = trade_map.get(cid, {})
        pos = pos_map.get(cid, {})
        
        data.append({
            "city": city.get("name", f"City {cid}"),
            "market_slug": risk.get("market_slug", ""),
            "market_probability": pred.get("market_probability"),
            "model_probability": pred.get("predicted_probability"),
            "raw_edge": pred.get("raw_edge"),
            "confidence": pred.get("confidence_score"),
            "risk_level": risk.get("risk_level", ""),
            "risk_decision": risk.get("risk_decision", ""),
            "trade_allowed": risk.get("trade_allowed", ""),
            "recommended_side": risk.get("recommended_side", ""),
            "paper_status": trade.get("status", ""),
            "position_status": pos.get("status", ""),
            "market_source": market_source_map.get(cid, ""),
        })

    df = dataframe_from_records(data)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data yet. Run the agent pipeline from the sidebar.")
