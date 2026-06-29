import streamlit as st
from dashboard.components import render_safety_banner, dataframe_from_records

def render(client):
    st.title("Predictions")
    render_safety_banner()

    latest = client.get_predictions_latest()
    cities = client.get_cities()

    if not latest:
        st.info("No predictions yet. Run the agent pipeline.")
        return

    st.subheader("Latest Predictions")
    df_latest = dataframe_from_records(latest)
    st.dataframe(df_latest, use_container_width=True)

    st.subheader("Prediction History")
    city_options = {c["name"]: c["id"] for c in cities}
    
    if not city_options:
        return
        
    selected_city = st.selectbox("Select a City", list(city_options.keys()))
    
    if selected_city:
        city_id = city_options[selected_city]
        history = client.get_prediction_history(city_id)
        if history:
            df_hist = dataframe_from_records(history)
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.write("No history available for this city.")
