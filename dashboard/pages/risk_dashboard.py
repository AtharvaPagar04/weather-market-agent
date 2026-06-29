import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.components import (
    render_safety_banner,
    render_page_header,
    dataframe_from_records,
    render_empty_state,
    render_decision_badge,
    render_status_badge,
    format_pct
)
from dashboard.charts import risk_decision_counts_chart

def render(client):
    render_page_header("Risk Dashboard", "Analysis of edge, liquidity, and confidence gating.")
    render_safety_banner()

    risk_reports = client.get_risk()
    cities = client.get_cities()
    city_map = {c["id"]: c["name"] for c in cities}

    if not risk_reports:
        render_empty_state("No risk reports available.")
        return

    st.header("1. Risk Summary")
    
    approved_count = sum(1 for r in risk_reports if r.get("trade_allowed"))
    watch_count = sum(1 for r in risk_reports if r.get("risk_decision") == "WATCH")
    no_trade_count = sum(1 for r in risk_reports if r.get("risk_decision") == "NO_TRADE")
    
    avg_confidence = sum(r.get("confidence", 0) for r in risk_reports) / len(risk_reports) if risk_reports else 0
    avg_size = sum(r.get("recommended_size", 0) for r in risk_reports) / len(risk_reports) if risk_reports else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Risk Reports", len(risk_reports))
    col2.metric("Approved Paper Actions", approved_count)
    col3.metric("Observation / WATCH", watch_count)
    col4.metric("No-Trade Count", no_trade_count)
    col5.metric("Average Confidence", f"{avg_confidence:.2f}")
    col6.metric("Avg Recommended Size", f"{avg_size:.2f}")
    
    st.header("2. Decision Distribution")
    colA, colB = st.columns(2)
    
    with colA:
        fig_decision = risk_decision_counts_chart(risk_reports)
        if fig_decision:
            st.plotly_chart(fig_decision, use_container_width=True)
            
    with colB:
        df_risk = dataframe_from_records(risk_reports)
        if not df_risk.empty and "risk_level" in df_risk.columns:
            counts = df_risk["risk_level"].value_counts().reset_index()
            counts.columns = ["Risk Level", "Count"]
            fig_level = px.pie(counts, values="Count", names="Risk Level", title="Risk Level Distribution")
            st.plotly_chart(fig_level, use_container_width=True)

    st.header("3. Risk-Gated Decisions")
    
    data = []
    for r in risk_reports:
        trade_allowed = r.get("trade_allowed", False)
        trade_allowed_str = "Approved" if trade_allowed else "Skipped / No paper order"
        
        risk_decision = r.get("risk_decision", "")
        if risk_decision == "WATCH":
            risk_decision = "Observation only — no paper order"
        else:
            risk_decision = render_decision_badge(risk_decision)

        data.append({
            "city": city_map.get(r.get("city_id"), str(r.get("city_id"))),
            "model_probability": format_pct(r.get("model_probability")),
            "market_probability": format_pct(r.get("market_probability")),
            "raw_edge": format_pct(r.get("raw_edge")),
            "tradeable_edge": format_pct(r.get("tradeable_edge")),
            "confidence": r.get("confidence"),
            "risk_level": render_status_badge(r.get("risk_level", "")),
            "risk_decision": risk_decision,
            "trade_allowed": trade_allowed_str,
            "recommended_side": r.get("recommended_side", ""),
            "recommended_size": r.get("recommended_size"),
            "blocked_reason": r.get("blocked_reason", ""),
            "reason": r.get("reason", ""),
        })

    df = dataframe_from_records(data)
    st.dataframe(df[["city", "model_probability", "market_probability", "raw_edge", "tradeable_edge", "confidence", "risk_level", "risk_decision", "trade_allowed", "recommended_side", "recommended_size"]], use_container_width=True)

    st.header("4. Blocked / Skipped Reasons")
    skipped_df = df[df["trade_allowed"] == "Skipped / No paper order"]
    if not skipped_df.empty:
        st.dataframe(skipped_df[["city", "risk_decision", "blocked_reason", "reason"]], use_container_width=True)
    else:
        render_empty_state("No reports were blocked or skipped.")
        
    st.header("5. Exposure Context")
    st.write("Displays the currently recommended paper sizes from the risk models.")
    st.dataframe(df[["city", "tradeable_edge", "recommended_size"]], use_container_width=True)
