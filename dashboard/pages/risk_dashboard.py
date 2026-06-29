import streamlit as st
from dashboard.components import render_safety_banner, dataframe_from_records

def render(client):
    st.title("Risk Dashboard")
    render_safety_banner()

    risk_reports = client.get_risk()
    cities = client.get_cities()
    city_map = {c["id"]: c["name"] for c in cities}

    if not risk_reports:
        st.info("No risk reports available.")
        return

    trade_allowed_count = sum(1 for r in risk_reports if r.get("trade_allowed"))
    blocked_count = len(risk_reports) - trade_allowed_count
    avg_confidence = sum(r.get("confidence", 0) for r in risk_reports) / len(risk_reports) if risk_reports else 0
    avg_size = sum(r.get("recommended_size", 0) for r in risk_reports) / len(risk_reports) if risk_reports else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Risk Reports", len(risk_reports))
    col2.metric("Trade Allowed", trade_allowed_count)
    col3.metric("Blocked/Skipped", blocked_count)
    col4.metric("Avg Confidence", f"{avg_confidence:.2f}")
    col5.metric("Avg Rec. Size", f"{avg_size:.2f}")

    st.subheader("Risk Reports Details")

    data = []
    for r in risk_reports:
        trade_allowed = r.get("trade_allowed", False)
        trade_allowed_str = str(trade_allowed) if trade_allowed else "Skipped / No paper order"
        
        risk_decision = r.get("risk_decision", "")
        if risk_decision == "WATCH":
            risk_decision = "WATCH (Observation only)"

        data.append({
            "city": city_map.get(r.get("city_id"), str(r.get("city_id"))),
            "model_probability": r.get("model_probability"),
            "market_probability": r.get("market_probability"),
            "raw_edge": r.get("raw_edge"),
            "tradeable_edge": r.get("tradeable_edge"),
            "confidence": r.get("confidence"),
            "risk_level": r.get("risk_level"),
            "risk_decision": risk_decision,
            "trade_allowed": trade_allowed_str,
            "recommended_side": r.get("recommended_side"),
            "recommended_size": r.get("recommended_size"),
            "blocked_reason": r.get("blocked_reason"),
            "reason": r.get("reason"),
        })

    df = dataframe_from_records(data)
    st.dataframe(df, use_container_width=True)
