import streamlit as st
import pandas as pd
from dashboard.components import (
    render_safety_banner,
    render_page_header,
    dataframe_from_records,
    render_decision_badge,
    render_status_badge,
    render_source_badge,
    render_empty_state,
    format_pct
)
from dashboard.charts import probability_comparison_chart, risk_decision_counts_chart, paper_order_status_chart

def render(client):
    render_page_header("Overview", "Main demo dashboard for the Weather Market Agent.")
    render_safety_banner()

    cities = client.get_cities()
    predictions = client.get_predictions_latest()
    risk_reports = client.get_risk()
    paper_trades = client.get_paper_trades()
    positions = client.get_positions()
    markets = client.get_markets()

    if not cities:
        render_empty_state("No data yet. Run the agent pipeline from the sidebar.")
        return

    st.header("1. System Snapshot")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Cities", len(cities))
    col2.metric("Latest Predictions", len(predictions))
    col3.metric("Risk Reports", len(risk_reports))
    col4.metric("Paper Orders Created", sum(1 for t in paper_trades if t.get("status") == "paper_order_created"))
    col5.metric("Paper Orders Skipped", sum(1 for t in paper_trades if t.get("status") == "paper_order_skipped"))
    col6.metric("Open Simulated Positions", sum(1 for p in positions if p.get("status") == "open"))

    st.header("2. Run Summary")
    st.write("Latest actions are visualized below.")
    
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    data = []
    pred_map = {p["city_id"]: p for p in predictions}
    risk_map = {r["city_id"]: r for r in risk_reports}
    trade_map = {}
    for t in sorted(paper_trades, key=lambda x: x.get("id", 0)):
        trade_map[t["city_id"]] = t
    pos_map = {}
    for p in positions:
        pos_map[p["city_id"]] = p
    market_source_map = {m["city_id"]: m.get("source", "unknown") for m in markets}

    for city in cities:
        cid = city["id"]
        cname = city.get("name", f"City {cid}")
        pred = pred_map.get(cid, {})
        risk = risk_map.get(cid, {})
        trade = trade_map.get(cid, {})
        pos = pos_map.get(cid, {})
        
        data.append({
            "city": cname,
            "market_slug": risk.get("market_slug", ""),
            "market_probability": pred.get("market_probability"),
            "model_probability": pred.get("predicted_probability"),
            "raw_edge": pred.get("raw_edge"),
            "confidence": pred.get("confidence_score"),
            "risk_level": render_status_badge(risk.get("risk_level", "")),
            "risk_decision": render_decision_badge(risk.get("risk_decision", "")),
            "trade_allowed": "Approved" if risk.get("trade_allowed") else "Skipped",
            "recommended_side": risk.get("recommended_side", ""),
            "paper_status": render_status_badge(trade.get("status", "")),
            "position_status": render_status_badge(pos.get("status", "")),
            "market_source": render_source_badge(market_source_map.get(cid, "")),
        })

    with chart_col1:
        fig_prob = probability_comparison_chart(data)
        if fig_prob:
            st.plotly_chart(fig_prob, use_container_width=True)
            
    with chart_col2:
        fig_risk = risk_decision_counts_chart(risk_reports)
        if fig_risk:
            st.plotly_chart(fig_risk, use_container_width=True)
            
    with chart_col3:
        fig_order = paper_order_status_chart(paper_trades)
        if fig_order:
            st.plotly_chart(fig_order, use_container_width=True)

    df = dataframe_from_records(data)
    
    if df.empty:
        render_empty_state("No data yet. Run the agent pipeline from the sidebar.")
        return
        
    df["market_probability"] = df["market_probability"].apply(format_pct)
    df["model_probability"] = df["model_probability"].apply(format_pct)
    df["raw_edge"] = df["raw_edge"].apply(format_pct)

    st.header("3. Market Watch")
    st.dataframe(df[["city", "market_slug", "market_source", "market_probability"]], use_container_width=True)
    
    st.header("4. Edge Matrix")
    st.dataframe(df[["city", "market_probability", "model_probability", "raw_edge", "confidence"]], use_container_width=True)
    
    st.header("5. Latest Paper Decisions")
    st.dataframe(df[["city", "risk_decision", "trade_allowed", "recommended_side", "paper_status"]], use_container_width=True)
    
    st.header("6. Open Simulated Positions")
    pos_df = df[df["position_status"] == "Open"]
    if not pos_df.empty:
        st.dataframe(pos_df[["city", "market_slug", "position_status"]], use_container_width=True)
    else:
        render_empty_state("No open simulated positions.")
