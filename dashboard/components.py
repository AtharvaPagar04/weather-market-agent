import streamlit as st
import pandas as pd


def render_safety_banner():
    st.warning("Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.", icon="⚠️")


def render_backend_status(client):
    if client.is_backend_available():
        st.sidebar.success("Backend: Online", icon="🟢")
    else:
        st.sidebar.error("Backend: Offline", icon="🔴")


def render_metric_card(label: str, value, help_text: str | None = None):
    st.metric(label=label, value=value, help=help_text)


def dataframe_from_records(records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame.from_records(records)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_pct(value):
    val = safe_float(value)
    return f"{val:.1%}"


def format_money(value):
    val = safe_float(value)
    return f"${val:.2f}"
