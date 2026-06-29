from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path("scripts/final_smoke_test.py")


def test_final_smoke_script_exists() -> None:
    assert SCRIPT_PATH.exists()


def test_final_smoke_script_contains_required_endpoint_checks() -> None:
    text = SCRIPT_PATH.read_text()

    for endpoint in (
        "/health",
        "/cities/seed",
        "/cities",
        "/agent/run",
        "/agent/runs",
        "/agent/logs",
        "/evaluation/summary",
        "/evaluation/run",
        "/demo/export",
        "/alerts/status",
        "/alerts/test",
    ):
        assert endpoint in text

    for file_name in (
        "demo_output",
        "results_summary.csv",
        "sample_predictions.json",
        "sample_orders.json",
        "pm_trader_stats.json",
    ):
        assert file_name in text


def test_final_smoke_script_contains_paper_only_safety_wording() -> None:
    text = SCRIPT_PATH.read_text()

    assert "Paper trading only" in text
    assert "simulated" in text
    assert "real-money orders" in text


def test_final_smoke_script_does_not_document_unsafe_routes() -> None:
    text = SCRIPT_PATH.read_text()

    blocked_literals = {
        "/orders" + "/place",
        "/trade" + "/execute",
        "/account" + "/connect",
        "/private" + "-key",
        "/wal" + "let",
    }
    for literal in blocked_literals:
        assert literal not in text


def test_final_smoke_script_runs_successfully() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "FINAL SMOKE TEST PASSED" in result.stdout
    assert "Backend health: PASS" in result.stdout
    assert "Agent pipeline: PASS" in result.stdout
    assert "Paper-only safety: PASS" in result.stdout
