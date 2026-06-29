import streamlit as st
import pandas as pd


def render_page_header(title: str, subtitle: str | None = None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_safety_banner():
    st.warning("Paper trading only — all execution shown is simulated. No real funds, wallets, private keys, signing credentials, or real-money orders are used.", icon="⚠️")


def render_backend_status(client):
    if client.is_backend_available():
        st.sidebar.success("Backend: Online", icon="🟢")
    else:
        st.sidebar.error("Backend: Offline", icon="🔴")


def render_metric_card(label: str, value, help_text: str | None = None):
    st.metric(label=label, value=value, help=help_text)


def render_status_badge(status: str) -> str:
    if not status:
        return ""
    return status.replace("_", " ").title()


def render_source_badge(source_type: str | None) -> str:
    if not source_type:
        return "Unknown"
    if source_type == "local_simulation":
        return "Local Simulation"
    return source_type.replace("_", " ").title()


def render_decision_badge(decision: str | None, trade_allowed: bool | None = None) -> str:
    if not decision:
        return ""
    if decision in ["PAPER_TRADE_SMALL", "PAPER_TRADE_NORMAL"]:
        return "Approved Paper Action"
    if decision == "WATCH":
        return "Observation Only"
    if decision in ["NO_TRADE", "MANUAL_REVIEW"]:
        return "Skipped"
    return decision


def render_empty_state(message: str):
    st.info(message, icon="ℹ️")


def dataframe_from_records(records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame.from_records(records)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def format_pct(value):
    if value is None:
        return ""
    val = safe_float(value)
    return f"{val:.1%}"


def format_money(value):
    if value is None:
        return ""
    val = safe_float(value)
    return f"${val:.2f}"
