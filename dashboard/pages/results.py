import streamlit as st
from dashboard.components import (
    render_safety_banner,
    render_page_header,
    render_empty_state
)
import os
import json
import csv

def render(client):
    render_page_header("Results / Evaluation", "Simulated model performance and export metrics.")
    render_safety_banner()
    
    st.info("Note: Realized weather outcomes are not available yet, so accuracy, Brier score, and log loss are not computed. Metrics shown are descriptive and purely simulated.")

    if st.button("Export Demo Data", type="primary"):
        with st.spinner("Exporting..."):
            res = client._post("/demo/export", data={}, fallback={})
            if res and res.get("status") == "success":
                st.success("Export successful!")
                for f in res.get("files_created", []):
                    st.write(f"- `{f}`")
            else:
                st.error("Export failed.")
                
    st.header("Evaluation Summary")
    summary = client._get("/evaluation/summary", fallback={})
    
    if not summary:
        render_empty_state("No summary available.")
        return
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Predictions", summary.get("predictions_count", 0))
    col2.metric("Cities Evaluated", summary.get("cities_evaluated", 0))
    col3.metric("Agent Runs", summary.get("agent_runs_count", 0))
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Average Model Probability", f"{summary.get('average_model_probability', 0):.2%}")
    col5.metric("Average Confidence", f"{summary.get('average_confidence', 0):.2f}")
    col6.metric("Total Risk Reports", summary.get("risk_reports_count", 0))
    
    col7, col8, col9 = st.columns(3)
    col7.metric("Paper Orders Created", summary.get("paper_orders_created", 0))
    col8.metric("Paper Orders Skipped", summary.get("paper_orders_skipped", 0))
    col9.metric("Simulated Positions", summary.get("simulated_positions_count", 0))

    st.subheader("Raw Summary Data")
    st.json(summary)
