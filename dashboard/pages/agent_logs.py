import streamlit as st
from dashboard.components import render_safety_banner, dataframe_from_records

def render(client):
    st.title("Agent Logs")
    render_safety_banner()

    runs = client.get_agent_runs()
    
    if not runs:
        st.info("No agent runs found.")
        return

    st.subheader("Latest Agent Runs")
    runs_data = []
    for r in runs:
        runs_data.append({
            "id": r.get("id"),
            "status": r.get("status"),
            "cities_processed": r.get("cities_processed"),
            "error_message": r.get("error_message"),
            "created_at": r.get("created_at"),
            "completed_at": r.get("completed_at"),
        })
    st.dataframe(dataframe_from_records(runs_data), use_container_width=True)

    st.subheader("Agent Step Logs")
    
    run_options = {f"Run {r['id']} ({r.get('status')})": r["id"] for r in runs}
    selected_run = st.selectbox("Select Agent Run", ["All"] + list(run_options.keys()))

    run_id = None if selected_run == "All" else run_options[selected_run]
    
    logs = client.get_agent_logs(run_id=run_id)
    
    if logs:
        # Check if Apify token missing/fallback used
        apify_missing = any("apify token" in str(l.get("message", "")).lower() for l in logs)
        if apify_missing:
            st.warning("Note: Apify token missing or fallback was used during this run.")

        # Filters
        col1, col2 = st.columns(2)
        statuses = list(set([l.get("status") for l in logs if l.get("status")]))
        steps = list(set([l.get("step_name") for l in logs if l.get("step_name")]))
        
        selected_status = col1.selectbox("Filter by Status", ["All"] + statuses)
        selected_step = col2.selectbox("Filter by Step Name", ["All"] + steps)
        
        filtered_logs = logs
        if selected_status != "All":
            filtered_logs = [l for l in filtered_logs if l.get("status") == selected_status]
        if selected_step != "All":
            filtered_logs = [l for l in filtered_logs if l.get("step_name") == selected_step]
            
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
        st.write("No logs for the selected run.")
