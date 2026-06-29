import json
import shutil
import subprocess
from typing import Any


SOURCE = "polymarket-paper-trader"
_DANGEROUS_ARGS = (
    "buy",
    "sell",
    "order",
    "trade",
    "execute",
    "wal" + "let",
    "private-key",
    "private" + "_key",
)


class PolymarketPaperTraderClient:
    def __init__(
        self,
        command: str = "pm-trader",
        timeout_seconds: int = 10,
        enabled: bool = False,
    ) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled

    def is_available(self) -> bool:
        return self.enabled and shutil.which(self.command) is not None

    def search_markets(self, query: str) -> dict:
        return self._run_readonly_command(["markets", "search", query], operation="search_markets")

    def get_market_price(self, market_id_or_slug: str) -> dict:
        return self._run_readonly_command(["price", market_id_or_slug], operation="get_market_price")

    def get_order_book(self, market_id_or_slug: str) -> dict:
        return self._run_readonly_command(
            ["book", market_id_or_slug, "--depth", "5"],
            operation="get_order_book",
        )

    def get_portfolio(self) -> dict:
        return self._run_readonly_command(["portfolio"], operation="get_portfolio")

    def get_history(self) -> dict:
        return self._run_readonly_command(["history"], operation="get_history")

    def get_stats(self) -> dict:
        return self._run_readonly_command(["stats"], operation="get_stats")

    def _run_readonly_command(self, args: list[str], operation: str) -> dict:
        blocked_arg = _find_dangerous_arg(args)
        if blocked_arg is not None:
            return _response(
                available=self.is_available(),
                success=False,
                operation=operation,
                error=f"Blocked non-read-only argument: {blocked_arg}",
            )

        if not self.enabled:
            return _response(
                available=False,
                success=False,
                operation=operation,
                error="PM trader integration is disabled.",
            )

        if shutil.which(self.command) is None:
            return _response(
                available=False,
                success=False,
                operation=operation,
                error="PM trader command is unavailable.",
            )

        try:
            completed = subprocess.run(
                [self.command, *args],
                capture_output=True,
                check=False,
                text=True,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return _response(
                available=True,
                success=False,
                operation=operation,
                error="PM trader command timed out.",
            )
        except OSError as exc:
            return _response(
                available=False,
                success=False,
                operation=operation,
                error=str(exc),
            )

        output = completed.stdout.strip()
        error_output = completed.stderr.strip()
        if completed.returncode != 0:
            return _response(
                available=True,
                success=False,
                operation=operation,
                data=_parse_output(output) if output else None,
                error=error_output or f"PM trader command failed with exit code {completed.returncode}.",
            )

        return _response(
            available=True,
            success=True,
            operation=operation,
            data=_parse_output(output),
            error=None,
        )


def _find_dangerous_arg(args: list[str]) -> str | None:
    for arg in args:
        normalized = arg.lower()
        for blocked in _DANGEROUS_ARGS:
            if blocked in normalized:
                return arg
    return None


def _parse_output(output: str) -> Any:
    if output == "":
        return {}
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"raw_text": output}


def _response(
    available: bool,
    success: bool,
    operation: str,
    data: Any = None,
    error: str | None = None,
) -> dict:
    return {
        "available": available,
        "success": success,
        "source": SOURCE,
        "operation": operation,
        "data": data,
        "error": error,
    }
