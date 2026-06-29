import plotly.express as px
import pandas as pd

def probability_comparison_chart(records):
    if not records:
        return None
    df = pd.DataFrame.from_records(records)
    if "city" not in df.columns or "model_probability" not in df.columns or "market_probability" not in df.columns:
        return None
    
    # Melt dataframe for plotly
    df_melted = df.melt(id_vars=["city"], value_vars=["model_probability", "market_probability"],
                        var_name="Type", value_name="Probability")
    
    # Format labels
    df_melted["Type"] = df_melted["Type"].replace({"model_probability": "Model Probability", "market_probability": "Market Probability"})
    
    fig = px.bar(df_melted, x="city", y="Probability", color="Type", barmode="group",
                 title="Model vs Market Probability by City", range_y=[0, 1])
    return fig

def risk_decision_counts_chart(risk_records):
    if not risk_records:
        return None
    df = pd.DataFrame.from_records(risk_records)
    if "risk_decision" not in df.columns:
        return None
        
    counts = df["risk_decision"].value_counts().reset_index()
    counts.columns = ["Risk Decision", "Count"]
    fig = px.pie(counts, values="Count", names="Risk Decision", title="Risk Decision Distribution")
    return fig

def paper_order_status_chart(order_records):
    if not order_records:
        return None
    df = pd.DataFrame.from_records(order_records)
    if "status" not in df.columns:
        return None
        
    counts = df["status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    fig = px.pie(counts, values="Count", names="Status", title="Paper Order Status Counts")
    return fig

def exposure_by_city_chart(position_records):
    if not position_records:
        return None
    df = pd.DataFrame.from_records(position_records)
    if "city" not in df.columns or "total_cost" not in df.columns:
        return None
        
    fig = px.bar(df, x="city", y="total_cost", title="Notional Exposure by City",
                 labels={"total_cost": "Total Simulated Cost ($)", "city": "City"})
    return fig
