import pytest
from dashboard.charts import (
    probability_comparison_chart,
    risk_decision_counts_chart,
    paper_order_status_chart,
    exposure_by_city_chart
)
import plotly.graph_objects as go

def test_charts_tolerate_empty_lists():
    assert probability_comparison_chart([]) is None
    assert risk_decision_counts_chart([]) is None
    assert paper_order_status_chart([]) is None
    assert exposure_by_city_chart([]) is None
    
    assert probability_comparison_chart(None) is None
    assert risk_decision_counts_chart(None) is None
    assert paper_order_status_chart(None) is None
    assert exposure_by_city_chart(None) is None

def test_charts_return_safe_objects():
    pred_data = [{"city": "Test", "model_probability": 0.5, "market_probability": 0.4}]
    risk_data = [{"risk_decision": "WATCH"}]
    order_data = [{"status": "paper_order_created"}]
    pos_data = [{"city": "Test", "total_cost": 100.0}]
    
    assert isinstance(probability_comparison_chart(pred_data), go.Figure)
    assert isinstance(risk_decision_counts_chart(risk_data), go.Figure)
    assert isinstance(paper_order_status_chart(order_data), go.Figure)
    assert isinstance(exposure_by_city_chart(pos_data), go.Figure)

def test_no_chart_helper_mutates_input_data():
    pred_data = [{"city": "Test", "model_probability": 0.5, "market_probability": 0.4}]
    pred_data_copy = [{"city": "Test", "model_probability": 0.5, "market_probability": 0.4}]
    probability_comparison_chart(pred_data)
    assert pred_data == pred_data_copy
    
    risk_data = [{"risk_decision": "WATCH"}]
    risk_data_copy = [{"risk_decision": "WATCH"}]
    risk_decision_counts_chart(risk_data)
    assert risk_data == risk_data_copy
    
    order_data = [{"status": "paper_order_created"}]
    order_data_copy = [{"status": "paper_order_created"}]
    paper_order_status_chart(order_data)
    assert order_data == order_data_copy
    
    pos_data = [{"city": "Test", "total_cost": 100.0}]
    pos_data_copy = [{"city": "Test", "total_cost": 100.0}]
    exposure_by_city_chart(pos_data)
    assert pos_data == pos_data_copy
