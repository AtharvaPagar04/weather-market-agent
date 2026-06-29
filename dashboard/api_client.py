import os
import requests

DEFAULT_BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


class BackendAPIClient:
    def __init__(self, base_url: str = DEFAULT_BACKEND_API_URL, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, endpoint: str, fallback: any):
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return fallback

    def _post(self, endpoint: str, data: dict, fallback: any):
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return fallback

    def is_backend_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2.0)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_health(self) -> dict:
        return self._get("/health", fallback={})

    def run_agent(self, force_mock_markets: bool = False, run_evaluation_after: bool = False) -> dict:
        return self._post(
            "/agent/run",
            data={"force_mock_markets": force_mock_markets, "run_evaluation_after": run_evaluation_after},
            fallback={"success": False, "status": "failed", "cities_processed": 0, "predictions_created": 0, "risk_reports_created": 0, "paper_orders_created": 0, "paper_orders_skipped": 0, "error_message": "Backend unavailable"},
        )

    def get_cities(self) -> list[dict]:
        return self._get("/cities", fallback=[])

    def get_weather_latest(self) -> list[dict]:
        return self._get("/weather/latest", fallback=[])

    def get_markets(self) -> list[dict]:
        return self._get("/markets", fallback=[])

    def get_predictions_latest(self) -> list[dict]:
        return self._get("/predictions/latest", fallback=[])

    def get_prediction_history(self, city_id: int, limit: int = 25) -> list[dict]:
        return self._get(f"/predictions/history/{city_id}?limit={limit}", fallback=[])

    def get_risk(self) -> list[dict]:
        return self._get("/risk", fallback=[])

    def get_paper_trades(self) -> list[dict]:
        return self._get("/paper-trades", fallback=[])

    def get_positions(self) -> list[dict]:
        return self._get("/positions", fallback=[])

    def get_agent_runs(self) -> list[dict]:
        return self._get("/agent-runs", fallback=[])

    def get_agent_logs(self, run_id: int | None = None) -> list[dict]:
        endpoint = f"/agent-logs?run_id={run_id}" if run_id else "/agent-logs"
        return self._get(endpoint, fallback=[])
