import streamlit as st
from dashboard.components import render_safety_banner, dataframe_from_records

def render(client):
    st.title("Paper Trades & Simulated Positions")
    render_safety_banner()

    paper_trades = client.get_paper_trades()
    positions = client.get_positions()
    cities = client.get_cities()
    city_map = {c["id"]: c["name"] for c in cities}

    created_count = sum(1 for t in paper_trades if t.get("status") == "paper_order_created")
    skipped_count = sum(1 for t in paper_trades if t.get("status") == "paper_order_skipped")
    local_sim_count = sum(1 for t in paper_trades if t.get("paper_execution_source") == "local_simulation")
    open_positions = sum(1 for p in positions if p.get("status") == "open")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Created Paper Orders", created_count)
    col2.metric("Skipped Decisions", skipped_count)
    col3.metric("Local Simulations", local_sim_count)
    col4.metric("Open Positions", open_positions)

    st.subheader("Paper Orders")
    if paper_trades:
        trades_data = []
        for t in paper_trades:
            trades_data.append({
                "city": city_map.get(t.get("city_id"), str(t.get("city_id"))),
                "market_slug": t.get("market_slug"),
                "side": t.get("side"),
                "simulated_price": t.get("simulated_price"),
                "size": t.get("size"),
                "notional_value": t.get("notional_value"),
                "edge": t.get("edge"),
                "risk_level": t.get("risk_level"),
                "status": t.get("status"),
                "paper_execution_source": "Local simulation" if t.get("paper_execution_source") == "local_simulation" else t.get("paper_execution_source"),
                "reason": t.get("reason"),
                "created_at": t.get("created_at"),
            })
        st.dataframe(dataframe_from_records(trades_data), use_container_width=True)
    else:
        st.info("No paper orders found.")

    st.subheader("Simulated Positions")
    if positions:
        pos_data = []
        for p in positions:
            pos_data.append({
                "city": city_map.get(p.get("city_id"), str(p.get("city_id"))),
                "market_slug": p.get("market_slug"),
                "side": p.get("side"),
                "total_size": p.get("total_size"),
                "average_price": p.get("average_price"),
                "current_market_price": p.get("current_market_price"),
                "total_cost": p.get("total_cost"),
                "unrealized_pnl": p.get("unrealized_pnl"),
                "status": p.get("status"),
            })
        st.dataframe(dataframe_from_records(pos_data), use_container_width=True)
    else:
        st.info("No simulated positions found.")
