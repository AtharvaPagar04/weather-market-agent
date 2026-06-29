import streamlit as st
from dashboard.components import (
    render_safety_banner,
    render_page_header,
    dataframe_from_records,
    render_empty_state
)

def render(client):
    render_page_header("Agent Logs", "Diagnostic information for the autonomous agent runs.")
    render_safety_banner()

    runs = client.get_agent_runs()
    
    if not runs:
        render_empty_state("No agent runs found.")
        return

    st.header("1. Latest Agent Runs")
    runs_data = []
    for r in runs:
        runs_data.append({
            "id": r.get("id"),
            "run_id": r.get("id"),
            "status": str(r.get("status", "")).title(),
            "cities_processed": r.get("cities_processed"),
            "weather_snapshots_created": r.get("weather_snapshots_created", 0),
            "market_snapshots_created": r.get("market_snapshots_created", 0),
            "predictions_created": r.get("predictions_created", 0),
            "risk_reports_created": r.get("risk_reports_created", 0),
            "paper_orders_created": r.get("paper_orders_created", 0),
            "paper_orders_skipped": r.get("paper_orders_skipped", 0),
            "started_at": r.get("created_at"),
            "finished_at": r.get("completed_at"),
        })
    st.dataframe(dataframe_from_records(runs_data), use_container_width=True)

    st.header("2. Agent Step Logs")
    
    run_options = {f"Run {r['id']} ({str(r.get('status', '')).title()})": r["id"] for r in runs}
    selected_run = st.selectbox("Select Agent Run", ["All"] + list(run_options.keys()))

    run_id = None if selected_run == "All" else run_options[selected_run]
    logs = client.get_agent_logs(run_id=run_id)
    
    if logs:
        st.header("3. Fallback and Warning Notes")
        
        apify_missing = any("apify token" in str(l.get("message", "")).lower() or "apify_api_token is not configured" in str(l.get("message", "")).lower() for l in logs)
        if apify_missing:
            st.warning("Apify is not configured. The pipeline continued with available global/local sources.")
            
        mock_market_fallback = any(l.get("fallback_used") for l in logs if "market" in str(l.get("step_name", "")).lower())
        if mock_market_fallback:
            st.info("Mock market fallback was used for demo continuity.")

        # Filters
        st.subheader("Filter Logs")
        col1, col2, col3 = st.columns(3)
        statuses = list(set([l.get("status") for l in logs if l.get("status")]))
        steps = list(set([l.get("step_name") for l in logs if l.get("step_name")]))
        fallbacks = ["All", "Yes", "No"]
        
        selected_status = col1.selectbox("Filter by Status", ["All"] + statuses)
        selected_step = col2.selectbox("Filter by Step Name", ["All"] + steps)
        selected_fallback = col3.selectbox("Filter by Fallback Used", fallbacks)
        
        filtered_logs = logs
        if selected_status != "All":
            filtered_logs = [l for l in filtered_logs if l.get("status") == selected_status]
        if selected_step != "All":
            filtered_logs = [l for l in filtered_logs if l.get("step_name") == selected_step]
        if selected_fallback != "All":
            fallback_val = (selected_fallback == "Yes")
            filtered_logs = [l for l in filtered_logs if bool(l.get("fallback_used")) == fallback_val]
            
        logs_data = []
        for l in filtered_logs:
            logs_data.append({
                "agent_run_id": l.get("agent_run_id"),
                "step_name": l.get("step_name"),
                "status": l.get("status"),
                "message": l.get("message"),
                "fallback_used": l.get("fallback_used"),
                "error_message": l.get("error_message"),
                "created_at": l.get("created_at"),
            })
            
        st.dataframe(dataframe_from_records(logs_data), use_container_width=True)
    else:
        render_empty_state("No logs for the selected run.")
