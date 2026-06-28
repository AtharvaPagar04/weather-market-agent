"""Validate documentation consistency for the WeatherAlgo planning docs.

Run:
    python scripts/validate_docs_consistency.py
    pytest tests/test_docs_consistency.py
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS_DIR = REPO_ROOT / "docs"

REQUIRED_ARCH_DOCS = (
    "docs/01_architecture.md",
    "docs/04_api_design.md",
    "docs/06_market_data_design.md",
    "docs/08_agent_orchestration.md",
    "docs/10_paper_trading.md",
    "docs/14_phase_wise_implementation_plan.md",
)

REQUIRED_ARCH_TERMS = (
    "polymarket-paper-trader",
    "PolymarketPaperTraderAdapter",
    "PolymarketMarketTool",
    "PolymarketPaperTradeTool",
)

PHASE_DOC = "docs/14_phase_wise_implementation_plan.md"
PHASE_REQUIRED_TERMS = (
    "Phase 4.5",
    "pm-trader init --balance 10000",
    "paper execution",
    "local DB audit mirror",
)

REFERENCE_DOC = "docs/15_reference_resources_analysis.md"
REFERENCE_REQUIRED_TERMS = (
    "polymarket-paper-trader",
    "PolyWeather",
    "Apify Weather Data Scraper",
    "reference-only",
    "Social media profit/copytrade claims are unverified",
    "No signing credential or funded-account configuration should exist in the MVP.",
)

RESOURCE_TERM_REQUIREMENTS = {
    "docs/08_agent_orchestration.md": (
        "Forecast vs Market Separation",
        "ForecastTool generates model probabilities from normalized weather signals only",
        "market leakage",
        "model_probability + market_probability",
    ),
    "docs/06_market_data_design.md": (
        "market-implied probability",
        "tradeable_edge",
        "slippage estimate",
    ),
    "docs/07_prediction_model.md": (
        "probability buckets",
        "confidence interval",
        "uncertainty penalty",
    ),
    "docs/09_risk_management.md": (
        "Tradeable Edge Formula",
        "raw_edge = model_probability - market_probability",
        "tradeable_edge = raw_edge - spread_cost - uncertainty_penalty - liquidity_penalty",
        "RiskService should prefer tradeable_edge",
        "NO_TRADE",
        "WATCH",
        "PAPER_TRADE_SMALL",
        "MANUAL_REVIEW",
    ),
    "docs/10_paper_trading.md": (
        "pm-trader and Local Audit Sync Handling",
        "Never submit the same pm-trader paper buy/sell twice",
        "audit_sync_status",
        "audit_sync_error",
    ),
    "docs/14_phase_wise_implementation_plan.md": (
        "Phase 4.5 prepares paper execution methods",
        "does not enable paper buy/sell workflow before RiskService approval exists",
        "DB-backed city endpoints belong to Phase 2",
        "agent_runs",
        "agent_run_logs",
        "Phase 6 - Risk Management",
        "Phase 7 - Paper Execution",
        "Phase 8 - Hermes Agent Orchestration",
        "Service-First Rule",
        "services first",
        "agent orchestration third",
    ),
}

DASHBOARD_DOC = "docs/11_dashboard_design.md"
DASHBOARD_REQUIRED_PANELS = (
    "Global Safety Warning Banner",
    "Paper trading only",
    "Market Watch",
    "Weather Evidence",
    "Probability Tracker",
    "Edge Matrix",
    "Paper Portfolio",
    "Transaction Feed",
)

EVALUATION_DOC = "docs/12_evaluation_metrics.md"
EVALUATION_REQUIRED_TERMS = (
    "Data Availability Metrics",
    "markets_matched_pct",
    "order_book_available_pct",
    "fallback_mock_market_pct",
    "weather_sources_available_pct",
    "Brier score",
    "calibration",
    "paper ROI",
    "max drawdown",
    "slippage",
)

SUBMISSION_DOC = "docs/13_submission_plan.md"
SUBMISSION_REQUIRED_TERMS = (
    "Resource Usage Disclosure",
    "polymarket-paper-trader",
    "PolyWeather",
    "Apify",
    "Social media posts",
    "No unverified ROI/profit claims",
    "No real-money trading",
)

MARKET_DOC = "docs/06_market_data_design.md"
MARKET_FALLBACK_PHRASES = (
    "mock market data is fallback-only",
    "mock market data is fallback/demo-only",
)
MARKET_PRIMARY_BAD_PATTERNS = (
    "mock market data is the primary",
    "mock market data as the primary",
    "mock market data will be the primary",
    "primary market data source:\nmock",
)

UNSAFE_TERMS = (
    "PRIVATE_KEY=",
    "WALLET_SECRET=",
    "real trade",
    "real order",
    "execute real",
    "funded account",
    "funded-account",
)

SAFETY_ALLOW_PHRASES = (
    "must not exist",
    "should not exist",
    "never places real-money orders",
    "not allowed in mvp",
    "no signing credential or funded-account configuration should exist in the mvp",
    "intentionally excluded",
    "excluded from the mvp",
    "out of scope",
    "never",
    "must not",
    "should not",
    "does not expose",
    "do not expose",
    "do not create",
    "do not add",
    "not require",
    "not expose",
    "not exist",
    "no private key",
    "no wallet",
    "no real order",
    "no non-paper",
    "cannot execute real-money",
    "no real funds",
)

RESOURCE_SAFETY_ALLOW_PHRASES = SAFETY_ALLOW_PHRASES + (
    "unverified",
    "must not be used",
    "should not be used",
    "strategy inspiration only",
    "inspiration only",
    "reference-only",
    "not as copied",
    "not copied",
    "not the only source",
    "future enhancement",
    "not mvp",
    "not in mvp",
    "will not build",
    "explicitly excluded",
    "excluded",
    "no copytrading",
    "no global globe-map",
    "no satellites",
    "no sports cv",
)

SCOPE_TERMS = (
    "globe map",
    "globe-map",
    "satellite",
    "satellites",
    "vessel",
    "vessels",
    "conflict tracking",
    "sports cv",
)


@dataclass(frozen=True)
class ValidationFailure:
    path: str
    reason: str
    line: int | None = None
    text: str | None = None

    def format(self) -> str:
        location = self.path
        if self.line is not None:
            location = f"{location}:{self.line}"
        message = f"{location}: {self.reason}"
        if self.text:
            message = f"{message}\n    {self.text.strip()}"
        return message


def load_docs(docs_dir: Path = DEFAULT_DOCS_DIR) -> dict[str, str]:
    """Load markdown docs with paths normalized as docs/<name>.md."""
    docs: dict[str, str] = {}
    for path in sorted(docs_dir.glob("*.md")):
        docs[f"docs/{path.name}"] = path.read_text(encoding="utf-8")
    return docs


def validate_required_arch_terms(docs: Mapping[str, str]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []
    for path in REQUIRED_ARCH_DOCS:
        text = docs.get(path)
        if text is None:
            failures.append(ValidationFailure(path, "required architecture doc is missing"))
            continue
        for term in REQUIRED_ARCH_TERMS:
            if term not in text:
                failures.append(
                    ValidationFailure(path, f"missing required architecture term: {term}")
                )
    return failures


def validate_phase_doc(docs: Mapping[str, str]) -> list[ValidationFailure]:
    text = docs.get(PHASE_DOC)
    if text is None:
        return [ValidationFailure(PHASE_DOC, "phase-wise implementation doc is missing")]

    failures: list[ValidationFailure] = []
    for term in PHASE_REQUIRED_TERMS:
        if term not in text:
            failures.append(ValidationFailure(PHASE_DOC, f"missing phase requirement: {term}"))
    return failures


def validate_market_fallback_only(docs: Mapping[str, str]) -> list[ValidationFailure]:
    text = docs.get(MARKET_DOC)
    if text is None:
        return [ValidationFailure(MARKET_DOC, "market data design doc is missing")]

    lower_text = text.lower()
    failures: list[ValidationFailure] = []
    if not any(phrase in lower_text for phrase in MARKET_FALLBACK_PHRASES):
        failures.append(
            ValidationFailure(
                MARKET_DOC,
                "mock market data must be described as fallback/demo-only",
            )
        )

    for pattern in MARKET_PRIMARY_BAD_PATTERNS:
        if pattern in lower_text:
            failures.append(
                ValidationFailure(
                    MARKET_DOC,
                    f"mock market data appears to be described as primary: {pattern}",
                )
            )
    return failures


def validate_reference_resource_doc(docs: Mapping[str, str]) -> list[ValidationFailure]:
    text = docs.get(REFERENCE_DOC)
    if text is None:
        return [ValidationFailure(REFERENCE_DOC, "reference resources analysis doc is missing")]

    failures: list[ValidationFailure] = []
    for term in REFERENCE_REQUIRED_TERMS:
        if term not in text:
            failures.append(
                ValidationFailure(REFERENCE_DOC, f"missing reference resource term: {term}")
            )
    return failures


def validate_resource_terms(docs: Mapping[str, str]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []
    for path, terms in RESOURCE_TERM_REQUIREMENTS.items():
        text = docs.get(path)
        if text is None:
            failures.append(ValidationFailure(path, "required resource-informed doc is missing"))
            continue
        for term in terms:
            if term not in text:
                failures.append(ValidationFailure(path, f"missing resource term: {term}"))
    return failures


def validate_dashboard_panels(docs: Mapping[str, str]) -> list[ValidationFailure]:
    text = docs.get(DASHBOARD_DOC)
    if text is None:
        return [ValidationFailure(DASHBOARD_DOC, "dashboard design doc is missing")]
    return [
        ValidationFailure(DASHBOARD_DOC, f"missing dashboard panel: {panel}")
        for panel in DASHBOARD_REQUIRED_PANELS
        if panel not in text
    ]


def validate_evaluation_metrics(docs: Mapping[str, str]) -> list[ValidationFailure]:
    text = docs.get(EVALUATION_DOC)
    if text is None:
        return [ValidationFailure(EVALUATION_DOC, "evaluation metrics doc is missing")]
    return [
        ValidationFailure(EVALUATION_DOC, f"missing evaluation metric: {term}")
        for term in EVALUATION_REQUIRED_TERMS
        if term not in text
    ]


def validate_submission_disclosure(docs: Mapping[str, str]) -> list[ValidationFailure]:
    text = docs.get(SUBMISSION_DOC)
    if text is None:
        return [ValidationFailure(SUBMISSION_DOC, "submission plan doc is missing")]
    return [
        ValidationFailure(SUBMISSION_DOC, f"missing resource usage disclosure term: {term}")
        for term in SUBMISSION_REQUIRED_TERMS
        if term not in text
    ]


def validate_resource_boundaries(docs: Mapping[str, str]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []
    for path, text in docs.items():
        lines = text.splitlines()
        lower_lines = [line.lower() for line in lines]
        for line_index, lower_line in enumerate(lower_lines):
            context = _context_window(lower_lines, line_index)
            if _line_has_bad_social_profit_claim(lower_line, context):
                failures.append(
                    ValidationFailure(
                        path,
                        "social media profit/ROI claims must not be target metrics",
                        line=line_index + 1,
                        text=lines[line_index],
                    )
                )
            if _line_has_bad_copytrade_claim(lower_line, context):
                failures.append(
                    ValidationFailure(
                        path,
                        "copytrade usage must not be included as project strategy",
                        line=line_index + 1,
                        text=lines[line_index],
                    )
                )
            if _line_has_bad_scope_requirement(lower_line, context):
                failures.append(
                    ValidationFailure(
                        path,
                        "out-of-scope resource is described as an MVP requirement",
                        line=line_index + 1,
                        text=lines[line_index],
                    )
                )
            if _line_has_bad_polyweather_copying(lower_line, context):
                failures.append(
                    ValidationFailure(
                        path,
                        "PolyWeather must be reference-only, not copied implementation",
                        line=line_index + 1,
                        text=lines[line_index],
                    )
                )
            if _line_has_bad_apify_only_source(lower_line, context):
                failures.append(
                    ValidationFailure(
                        path,
                        "Apify must be documented as one source, not the only source",
                        line=line_index + 1,
                        text=lines[line_index],
                    )
                )
    return failures


def validate_safety_terms(docs: Mapping[str, str]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []
    for path, text in docs.items():
        lines = text.splitlines()
        lower_lines = [line.lower() for line in lines]
        for line_index, lower_line in enumerate(lower_lines):
            for term in UNSAFE_TERMS:
                if term.lower() not in lower_line:
                    continue
                context = _context_window(lower_lines, line_index)
                if _is_allowed_safety_context(context):
                    continue
                failures.append(
                    ValidationFailure(
                        path,
                        f"unsafe term is not clearly safety-oriented: {term}",
                        line=line_index + 1,
                        text=lines[line_index],
                    )
                )
    return failures


def validate_docs(docs: Mapping[str, str]) -> list[ValidationFailure]:
    failures: list[ValidationFailure] = []
    failures.extend(validate_required_arch_terms(docs))
    failures.extend(validate_phase_doc(docs))
    failures.extend(validate_reference_resource_doc(docs))
    failures.extend(validate_resource_terms(docs))
    failures.extend(validate_dashboard_panels(docs))
    failures.extend(validate_evaluation_metrics(docs))
    failures.extend(validate_submission_disclosure(docs))
    failures.extend(validate_market_fallback_only(docs))
    failures.extend(validate_resource_boundaries(docs))
    failures.extend(validate_safety_terms(docs))
    return failures


def print_summary(failures: Sequence[ValidationFailure]) -> None:
    if not failures:
        print("PASS: documentation consistency validation succeeded.")
        return

    print(f"FAIL: documentation consistency validation found {len(failures)} issue(s).")
    for failure in failures:
        print(f"- {failure.format()}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=DEFAULT_DOCS_DIR,
        help="Directory containing markdown docs. Defaults to ./docs.",
    )
    args = parser.parse_args(argv)

    if not args.docs_dir.exists():
        print(f"FAIL: docs directory does not exist: {args.docs_dir}")
        return 1

    failures = validate_docs(load_docs(args.docs_dir))
    print_summary(failures)
    return 1 if failures else 0


def _context_window(lines: Sequence[str], line_index: int, radius: int = 5) -> str:
    start = max(0, line_index - radius)
    end = min(len(lines), line_index + radius + 1)
    return "\n".join(lines[start:end])


def _is_allowed_safety_context(context: str) -> bool:
    return any(phrase in context for phrase in SAFETY_ALLOW_PHRASES)


def _is_allowed_resource_context(context: str) -> bool:
    return any(phrase in context for phrase in RESOURCE_SAFETY_ALLOW_PHRASES)


def _line_has_bad_social_profit_claim(lower_line: str, context: str) -> bool:
    has_social = "social media" in lower_line
    has_performance = any(term in lower_line for term in ("profit", "roi", "performance"))
    has_target = any(
        term in lower_line
        for term in ("target", "expected", "guaranteed", "project result", "results")
    )
    return has_social and has_performance and has_target and not _is_allowed_resource_context(context)


def _line_has_bad_copytrade_claim(lower_line: str, context: str) -> bool:
    has_copytrade = any(term in lower_line for term in ("copytrade", "copytrading", "copy trade"))
    return has_copytrade and not _is_allowed_resource_context(context)


def _line_has_bad_scope_requirement(lower_line: str, context: str) -> bool:
    has_scope_term = any(term in lower_line for term in SCOPE_TERMS)
    has_mvp_requirement = any(term in lower_line for term in ("mvp", "required", "requirement", "build"))
    return has_scope_term and has_mvp_requirement and not _is_allowed_resource_context(context)


def _line_has_bad_polyweather_copying(lower_line: str, context: str) -> bool:
    has_polyweather = "polyweather" in lower_line
    has_copying = any(term in lower_line for term in ("copy", "copied", "code", "implementation"))
    return has_polyweather and has_copying and not _is_allowed_resource_context(context)


def _line_has_bad_apify_only_source(lower_line: str, context: str) -> bool:
    has_apify = "apify" in lower_line
    has_only_source = any(
        term in lower_line
        for term in ("only source", "single source", "sole source", "the weather source")
    )
    return has_apify and has_only_source and not _is_allowed_resource_context(context)


if __name__ == "__main__":
    sys.exit(main())
