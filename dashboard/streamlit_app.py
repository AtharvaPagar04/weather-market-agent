import streamlit as st

st.set_page_config(
    page_title="Weather Market Agent",
    page_icon="🌦️",
    layout="wide",
)

from dashboard.api_client import BackendAPIClient
from dashboard.components import render_backend_status
from dashboard.pages import overview, predictions, risk_dashboard, paper_trades, agent_logs, results
import datetime

def main():
    client = BackendAPIClient()

    st.sidebar.title("Weather Market Agent")
    render_backend_status(client)
    
    st.sidebar.caption(f"Last Refreshed: {datetime.datetime.now().strftime('%H:%M:%S')}")

    force_mock_markets = st.sidebar.checkbox("Force mock markets", value=False)
    run_clicked = st.sidebar.button("Run Agent Pipeline")
    
    if run_clicked:
        with st.spinner("Running Agent Pipeline..."):
            result = client.run_agent(force_mock_markets=force_mock_markets)
            if result.get("success") or result.get("status") == "partial":
                st.sidebar.success(f"Run {result.get('status', 'completed')}")
                st.sidebar.write(f"Cities processed: {result.get('cities_processed', 0)}")
                st.sidebar.write(f"Weather Snapshots: {result.get('weather_snapshots_created', 0)}")
                st.sidebar.write(f"Market Snapshots: {result.get('market_snapshots_created', 0)}")
                st.sidebar.write(f"Predictions: {result.get('predictions_created', 0)}")
                st.sidebar.write(f"Risk Reports: {result.get('risk_reports_created', 0)}")
                st.sidebar.write(f"Orders Created: {result.get('paper_orders_created', 0)}")
                st.sidebar.write(f"Orders Skipped: {result.get('paper_orders_skipped', 0)}")
                if "Apify token" in str(result):
                    st.sidebar.warning("Note: Apify token missing/fallback used.")
            else:
                st.sidebar.error("Failed to run agent")

    refresh_clicked = st.sidebar.button("Refresh Dashboard")
    if refresh_clicked:
        st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Predictions", "Risk Dashboard", "Paper Trades", "Agent Logs", "Results / Evaluation"]
    )

    if page == "Overview":
        overview.render(client)
    elif page == "Predictions":
        predictions.render(client)
    elif page == "Risk Dashboard":
        risk_dashboard.render(client)
    elif page == "Paper Trades":
        paper_trades.render(client)
    elif page == "Agent Logs":
        agent_logs.render(client)
    elif page == "Results / Evaluation":
        results.render(client)


if __name__ == "__main__":
    main()
