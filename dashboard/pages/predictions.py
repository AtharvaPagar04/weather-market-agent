import streamlit as st
from dashboard.components import (
    render_safety_banner,
    render_page_header,
    dataframe_from_records,
    render_empty_state,
    format_pct
)
from dashboard.charts import probability_comparison_chart

def render(client):
    render_page_header("Predictions", "Latest prediction signals and probability tracker.")
    render_safety_banner()

    latest = client.get_predictions_latest()
    cities = client.get_cities()
    city_map = {c["id"]: c["name"] for c in cities}

    if not latest:
        render_empty_state("No predictions yet. Run the agent pipeline.")
        return

    st.header("1. Latest Predictions")
    
    data = []
    for p in latest:
        data.append({
            "City": city_map.get(p.get("city_id"), str(p.get("city_id"))),
            "Model Probability": format_pct(p.get("predicted_probability")),
            "Market Probability": format_pct(p.get("market_probability")),
            "Raw Edge": format_pct(p.get("raw_edge")),
            "Confidence": p.get("confidence_score"),
            "Prediction Label": p.get("prediction_label", "").replace("_", " ").title(),
            "Explanation": p.get("explanation", ""),
            "created_at": p.get("created_at"),
            "city_id": p.get("city_id"),
            "model_probability": p.get("predicted_probability"),
            "market_probability": p.get("market_probability")
        })
        
    df_latest = dataframe_from_records(data)
    
    st.dataframe(df_latest[["City", "Model Probability", "Market Probability", "Raw Edge", "Confidence", "Prediction Label"]], use_container_width=True)

    st.header("2. Probability Tracker")
    chart_data = [{"city": row["City"], "model_probability": row["model_probability"], "market_probability": row["market_probability"]} for row in data]
    fig = probability_comparison_chart(chart_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
    st.header("3. Prediction History by City")
    city_options = {c["name"]: c["id"] for c in cities}
    
    if city_options:
        selected_city = st.selectbox("Select a City", list(city_options.keys()))
        
        if selected_city:
            city_id = city_options[selected_city]
            history = client.get_prediction_history(city_id)
            if history:
                hist_data = []
                for p in history:
                    hist_data.append({
                        "Created At": p.get("created_at"),
                        "Model Probability": format_pct(p.get("predicted_probability")),
                        "Market Probability": format_pct(p.get("market_probability")),
                        "Raw Edge": format_pct(p.get("raw_edge")),
                        "Confidence": p.get("confidence_score"),
                        "Prediction Label": p.get("prediction_label", "").replace("_", " ").title(),
                    })
                df_hist = dataframe_from_records(hist_data)
                st.dataframe(df_hist, use_container_width=True)
            else:
                render_empty_state("No history available for this city.")
                
    st.header("4. Explanation Table")
    st.dataframe(df_latest[["City", "Explanation"]], use_container_width=True)
