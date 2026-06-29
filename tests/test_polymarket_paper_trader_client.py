import subprocess

from app.integrations.polymarket_paper_trader_client import PolymarketPaperTraderClient


def test_disabled_client_returns_unavailable_without_subprocess(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(subprocess, "run", fail_if_called)

    result = PolymarketPaperTraderClient(enabled=False).search_markets("weather")

    assert result["available"] is False
    assert result["success"] is False
    assert result["error"] == "PM trader integration is disabled."


def test_missing_command_returns_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda command: None)

    result = PolymarketPaperTraderClient(enabled=True).search_markets("weather")

    assert result["available"] is False
    assert result["success"] is False
    assert result["error"] == "PM trader command is unavailable."


def test_readonly_command_blocks_dangerous_args(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda command: "/usr/bin/pm-trader")

    result = PolymarketPaperTraderClient(enabled=True).search_markets("weather buy")

    assert result["success"] is False
    assert "Blocked non-read-only argument" in result["error"]


def test_json_output_is_parsed_safely(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda command: "/usr/bin/pm-trader")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, stdout='{"markets":[{"id":"1"}]}', stderr=""),
    )

    result = PolymarketPaperTraderClient(enabled=True).search_markets("weather")

    assert result["success"] is True
    assert result["data"] == {"markets": [{"id": "1"}]}


def test_non_json_output_is_returned_as_raw_text(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda command: "/usr/bin/pm-trader")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, stdout="plain output", stderr=""),
    )

    result = PolymarketPaperTraderClient(enabled=True).get_stats()

    assert result["success"] is True
    assert result["data"] == {"raw_text": "plain output"}


def test_timeout_returns_structured_error(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda command: "/usr/bin/pm-trader")

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=10)

    monkeypatch.setattr(subprocess, "run", raise_timeout)

    result = PolymarketPaperTraderClient(enabled=True).get_stats()

    assert result["available"] is True
    assert result["success"] is False
    assert result["error"] == "PM trader command timed out."
