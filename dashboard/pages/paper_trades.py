import streamlit as st
from dashboard.components import (
    render_safety_banner,
    render_page_header,
    dataframe_from_records,
    render_empty_state,
    format_pct,
    format_money
)
from dashboard.charts import paper_order_status_chart, exposure_by_city_chart

def render(client):
    render_page_header("Paper Trades", "Review simulated orders and virtual exposure.")
    render_safety_banner()

    paper_trades = client.get_paper_trades()
    positions = client.get_positions()
    cities = client.get_cities()
    city_map = {c["id"]: c["name"] for c in cities}

    st.header("1. Paper Trading Summary")

    created_count = sum(1 for t in paper_trades if t.get("status") == "paper_order_created")
    skipped_count = sum(1 for t in paper_trades if t.get("status") == "paper_order_skipped")
    local_sim_count = sum(1 for t in paper_trades if t.get("paper_execution_source") == "local_simulation")
    
    open_positions = sum(1 for p in positions if p.get("status") == "open")
    total_simulated_cost = sum(p.get("total_cost", 0) for p in positions if p.get("status") == "open")
    est_unrealized_pnl = sum(p.get("unrealized_pnl", 0) for p in positions if p.get("status") == "open")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Created Paper Orders", created_count)
    col2.metric("Skipped Paper Decisions", skipped_count)
    col3.metric("Local Simulation Orders", local_sim_count)
    col4.metric("Open Simulated Positions", open_positions)
    col5.metric("Total Simulated Cost", format_money(total_simulated_cost))
    col6.metric("Estimated Unrealized PnL", format_money(est_unrealized_pnl))
    
    colA, colB = st.columns(2)
    with colA:
        fig_orders = paper_order_status_chart(paper_trades)
        if fig_orders:
            st.plotly_chart(fig_orders, width="stretch")
            
    with colB:
        pos_for_chart = []
        for p in positions:
            pos_for_chart.append({
                "city": city_map.get(p.get("city_id"), str(p.get("city_id"))),
                "total_cost": p.get("total_cost", 0)
            })
        fig_exp = exposure_by_city_chart(pos_for_chart)
        if fig_exp:
            st.plotly_chart(fig_exp, width="stretch")

    st.header("2. Paper Orders / Skipped Decisions")
    if paper_trades:
        trades_data = []
        for t in paper_trades:
            source = t.get("paper_execution_source", "")
            if source == "local_simulation":
                source = "Local simulation"
                
            trades_data.append({
                "city": city_map.get(t.get("city_id"), str(t.get("city_id"))),
                "market_slug": t.get("market_slug", ""),
                "side": t.get("side", ""),
                "simulated_price": t.get("simulated_price"),
                "size": t.get("size"),
                "notional_value": format_money(t.get("notional_value")),
                "edge": format_pct(t.get("edge")),
                "risk_level": str(t.get("risk_level", "")).title(),
                "status": t.get("status", ""),
                "paper_execution_source": source,
                "reason": t.get("reason", ""),
                "created_at": t.get("created_at"),
            })
        st.dataframe(dataframe_from_records(trades_data), width="stretch")
    else:
        render_empty_state("No paper orders found.")

    st.header("3. Simulated Positions")
    if positions:
        pos_data = []
        for p in positions:
            pos_data.append({
                "city": city_map.get(p.get("city_id"), str(p.get("city_id"))),
                "market_slug": p.get("market_slug", ""),
                "side": p.get("side", ""),
                "total_size": p.get("total_size"),
                "average_price": p.get("average_price"),
                "current_market_price": p.get("current_market_price"),
                "total_cost": format_money(p.get("total_cost")),
                "unrealized_pnl": format_money(p.get("unrealized_pnl")),
                "status": str(p.get("status", "")).title(),
            })
        st.dataframe(dataframe_from_records(pos_data), width="stretch")
    else:
        render_empty_state("No simulated positions found.")
        
    st.header("4. Local Audit Notes")
    st.info("Paper executions shown above use standard simulated pricing and do not dispatch network orders unless a dedicated paper trading provider is configured.")
