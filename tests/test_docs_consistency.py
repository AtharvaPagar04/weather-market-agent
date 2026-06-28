from __future__ import annotations

from scripts.validate_docs_consistency import (
    DASHBOARD_DOC,
    DASHBOARD_REQUIRED_PANELS,
    EVALUATION_DOC,
    EVALUATION_REQUIRED_TERMS,
    MARKET_DOC,
    PHASE_DOC,
    REFERENCE_DOC,
    REFERENCE_REQUIRED_TERMS,
    REQUIRED_ARCH_DOCS,
    REQUIRED_ARCH_TERMS,
    RESOURCE_TERM_REQUIREMENTS,
    SUBMISSION_DOC,
    SUBMISSION_REQUIRED_TERMS,
    validate_dashboard_panels,
    validate_docs,
    validate_evaluation_metrics,
    validate_market_fallback_only,
    validate_reference_resource_doc,
    validate_required_arch_terms,
    validate_resource_boundaries,
    validate_resource_terms,
    validate_safety_terms,
)


def test_current_docs_pass_validation() -> None:
    from scripts.validate_docs_consistency import load_docs

    failures = validate_docs(load_docs())

    assert failures == []


def test_missing_required_architecture_term_is_reported() -> None:
    docs = _valid_doc_set()
    docs["docs/01_architecture.md"] = docs["docs/01_architecture.md"].replace(
        "PolymarketPaperTraderAdapter", ""
    )

    failures = validate_required_arch_terms(docs)

    assert any(
        failure.path == "docs/01_architecture.md"
        and "PolymarketPaperTraderAdapter" in failure.reason
        for failure in failures
    )


def test_missing_reference_resources_analysis_doc_fails() -> None:
    docs = _valid_doc_set()
    docs.pop(REFERENCE_DOC)

    failures = validate_reference_resource_doc(docs)

    assert any("reference resources analysis doc is missing" in failure.reason for failure in failures)


def test_missing_resource_terms_fail() -> None:
    docs = _valid_doc_set()
    docs["docs/07_prediction_model.md"] = docs["docs/07_prediction_model.md"].replace(
        "confidence interval", ""
    )

    failures = validate_resource_terms(docs)

    assert any("confidence interval" in failure.reason for failure in failures)


def test_missing_forecast_market_separation_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/08_agent_orchestration.md"] = docs["docs/08_agent_orchestration.md"].replace(
        "Forecast vs Market Separation", ""
    )

    failures = validate_resource_terms(docs)

    assert any("Forecast vs Market Separation" in failure.reason for failure in failures)


def test_missing_service_first_rule_fails() -> None:
    docs = _valid_doc_set()
    docs[PHASE_DOC] = docs[PHASE_DOC].replace("Service-First Rule", "")

    failures = validate_resource_terms(docs)

    assert any("Service-First Rule" in failure.reason for failure in failures)


def test_missing_tradeable_edge_formula_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/09_risk_management.md"] = docs["docs/09_risk_management.md"].replace(
        "Tradeable Edge Formula", ""
    )

    failures = validate_resource_terms(docs)

    assert any("Tradeable Edge Formula" in failure.reason for failure in failures)


def test_missing_audit_sync_status_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/10_paper_trading.md"] = docs["docs/10_paper_trading.md"].replace(
        "audit_sync_status", ""
    )

    failures = validate_resource_terms(docs)

    assert any("audit_sync_status" in failure.reason for failure in failures)


def test_market_doc_requires_mock_fallback_only_wording() -> None:
    docs = _valid_doc_set()
    docs[MARKET_DOC] = docs[MARKET_DOC].replace(
        "Mock market data is fallback-only.",
        "Mock market data is the primary market source.",
    )

    failures = validate_market_fallback_only(docs)

    assert any("fallback/demo-only" in failure.reason for failure in failures)
    assert any("described as primary" in failure.reason for failure in failures)


def test_unsafe_social_media_performance_claim_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/bad.md"] = "Social media profit claims are expected target metrics.\n"

    failures = validate_resource_boundaries(docs)

    assert any("social media profit/ROI claims" in failure.reason for failure in failures)


def test_copytrade_usage_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/bad.md"] = "The strategy should use copytrade signals from social posts.\n"

    failures = validate_resource_boundaries(docs)

    assert any("copytrade usage" in failure.reason for failure in failures)


def test_globe_satellite_vessel_conflict_tracking_as_mvp_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/bad.md"] = "The MVP must build globe map satellite and vessel conflict tracking.\n"

    failures = validate_resource_boundaries(docs)

    assert any("out-of-scope resource" in failure.reason for failure in failures)


def test_polyweather_copied_code_wording_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/bad.md"] = "Copy PolyWeather code and implementation into this project.\n"

    failures = validate_resource_boundaries(docs)

    assert any("PolyWeather must be reference-only" in failure.reason for failure in failures)


def test_polyweather_reference_only_wording_passes() -> None:
    docs = {
        "docs/safe.md": "PolyWeather is reference-only and not copied implementation.\n"
    }

    failures = validate_resource_boundaries(docs)

    assert failures == []


def test_apify_as_one_source_passes() -> None:
    docs = {
        "docs/safe.md": "The Apify Weather Data Scraper is one weather ingestion source, not the only source.\n"
    }

    failures = validate_resource_boundaries(docs)

    assert failures == []


def test_apify_as_only_source_fails() -> None:
    docs = _valid_doc_set()
    docs["docs/bad.md"] = "Apify is the only source for all weather data.\n"

    failures = validate_resource_boundaries(docs)

    assert any("Apify must be documented as one source" in failure.reason for failure in failures)


def test_terminal_dashboard_required_panels_are_enforced() -> None:
    docs = _valid_doc_set()
    docs[DASHBOARD_DOC] = docs[DASHBOARD_DOC].replace("Market Watch", "")

    failures = validate_dashboard_panels(docs)

    assert any("Market Watch" in failure.reason for failure in failures)


def test_global_safety_warning_banner_is_enforced() -> None:
    docs = _valid_doc_set()
    docs[DASHBOARD_DOC] = docs[DASHBOARD_DOC].replace("Global Safety Warning Banner", "")

    failures = validate_dashboard_panels(docs)

    assert any("Global Safety Warning Banner" in failure.reason for failure in failures)


def test_evaluation_metrics_are_enforced() -> None:
    docs = _valid_doc_set()
    docs[EVALUATION_DOC] = docs[EVALUATION_DOC].replace("Brier score", "")

    failures = validate_evaluation_metrics(docs)

    assert any("Brier score" in failure.reason for failure in failures)


def test_data_availability_metrics_are_enforced() -> None:
    docs = _valid_doc_set()
    docs[EVALUATION_DOC] = docs[EVALUATION_DOC].replace("Data Availability Metrics", "")

    failures = validate_evaluation_metrics(docs)

    assert any("Data Availability Metrics" in failure.reason for failure in failures)


def test_unsafe_wording_without_safety_context_is_reported() -> None:
    docs = _valid_doc_set()
    docs["docs/bad.md"] = "Configure PRIVATE_KEY=abc before running the MVP.\n"

    failures = validate_safety_terms(docs)

    assert any(
        failure.path == "docs/bad.md"
        and "PRIVATE_KEY=" in failure.reason
        for failure in failures
    )


def test_safety_negative_wording_still_passes() -> None:
    docs = {
        "docs/safe.md": (
            "Safety validation:\n"
            "No signing credential or funded-account configuration should exist in the MVP.\n"
        )
    }

    failures = validate_safety_terms(docs)

    assert failures == []


def _valid_doc_set() -> dict[str, str]:
    architecture_terms = "\n".join(REQUIRED_ARCH_TERMS)
    docs = {path: f"{architecture_terms}\n" for path in REQUIRED_ARCH_DOCS}
    docs[PHASE_DOC] = (
        f"{docs[PHASE_DOC]}\n"
        "Phase 4.5\n"
        "pm-trader init --balance 10000\n"
        "paper execution\n"
        "local DB audit mirror\n"
        "Phase 4.5 prepares paper execution methods\n"
        "does not enable paper buy/sell workflow before RiskService approval exists\n"
        "DB-backed city endpoints belong to Phase 2\n"
        "agent_runs\n"
        "agent_run_logs\n"
    )
    docs[MARKET_DOC] = (
        f"{docs[MARKET_DOC]}\n"
        "Primary market data source:\n"
        "polymarket-paper-trader\n"
        "Mock market data is fallback-only.\n"
    )
    docs[REFERENCE_DOC] = "\n".join(REFERENCE_REQUIRED_TERMS)
    for path, terms in RESOURCE_TERM_REQUIREMENTS.items():
        docs[path] = f"{docs.get(path, '')}\n" + "\n".join(terms)
    docs[DASHBOARD_DOC] = f"{docs.get(DASHBOARD_DOC, '')}\n" + "\n".join(
        DASHBOARD_REQUIRED_PANELS
    )
    docs[EVALUATION_DOC] = f"{docs.get(EVALUATION_DOC, '')}\n" + "\n".join(
        EVALUATION_REQUIRED_TERMS
    )
    docs[SUBMISSION_DOC] = f"{docs.get(SUBMISSION_DOC, '')}\n" + "\n".join(
        SUBMISSION_REQUIRED_TERMS
    )
    return docs
