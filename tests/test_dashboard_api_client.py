import os
import requests
from unittest.mock import patch, Mock
import pytest

from dashboard.api_client import BackendAPIClient

def test_client_builds_base_url():
    client = BackendAPIClient(base_url="http://test-server:8000/")
    assert client.base_url == "http://test-server:8000"

@patch("requests.get")
def test_get_health_calls_health_endpoint(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    client = BackendAPIClient(base_url="http://test")
    res = client.get_health()
    
    assert res == {"status": "ok"}
    mock_get.assert_called_once_with("http://test/health", timeout=10.0)

@patch("requests.post")
def test_run_agent_calls_agent_run(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    client = BackendAPIClient(base_url="http://test")
    res = client.run_agent(force_mock_markets=True)
    
    assert res == {"success": True}
    mock_post.assert_called_once_with(
        "http://test/agent/run", 
        json={"force_mock_markets": True, "run_evaluation_after": False}, 
        timeout=10.0
    )

@patch("requests.get")
def test_get_prediction_history_calls_correct_endpoint(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": 1}]
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    client = BackendAPIClient(base_url="http://test")
    res = client.get_prediction_history(city_id=1)
    
    assert res == [{"id": 1}]
    mock_get.assert_called_once_with("http://test/predictions/history/1?limit=25", timeout=10.0)

@patch("requests.get")
def test_list_endpoints_return_empty_list_on_failure(mock_get):
    mock_get.side_effect = requests.RequestException("Connection error")
    client = BackendAPIClient()
    
    assert client.get_cities() == []
    assert client.get_weather_latest() == []
    assert client.get_markets() == []
    assert client.get_predictions_latest() == []
    assert client.get_prediction_history(city_id=1) == []
    assert client.get_risk() == []
    assert client.get_paper_trades() == []
    assert client.get_positions() == []
    assert client.get_agent_runs() == []
    assert client.get_agent_logs() == []

@patch("requests.get")
def test_object_endpoints_return_empty_dict_on_failure(mock_get):
    mock_get.side_effect = requests.RequestException("Connection error")
    client = BackendAPIClient()
    
    assert client.get_health() == {}

def test_no_forbidden_endpoints_in_api_client():
    forbidden = [
        "/orders/place",
        "/trade/execute",
        "/account/connect",
        "/private-key",
        "/wallet",
        "/paper-trader/buy",
        "/paper-trader/sell",
        "/paper-trader/order",
    ]
    with open("dashboard/api_client.py", "r") as f:
        content = f.read()
    
    for endpoint in forbidden:
        assert endpoint not in content, f"Forbidden endpoint {endpoint} found in api_client.py"
