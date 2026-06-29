MAX_TRADE_RISK_PCT = 0.02
MAX_TOTAL_EXPOSURE_PCT = 0.10
FRACTIONAL_KELLY_MULTIPLIER = 0.25


class RiskCalculator:
    def analyze(self, prediction, market_snapshot, bankroll: float = 1000.0) -> dict:
        model_probability = _probability(_first_present(prediction, ("model_probability", "predicted_probability")))
        market_probability = _probability(
            _first_present(prediction, ("market_probability",))
            if _first_present(prediction, ("market_probability",)) is not None
            else _first_present(market_snapshot, ("implied_probability", "yes_price"))
        )
        confidence = _clamp(float(_first_present(prediction, ("confidence_score", "confidence")) or 0.0), 0, 1)
        raw_edge = model_probability - market_probability
        spread_cost = max(float(_first_present(market_snapshot, ("spread",)) or 0.0), 0.0)
        uncertainty_penalty = max(0.0, 0.60 - confidence) * 0.5
        liquidity_score, liquidity_penalty = _liquidity_score_and_penalty(market_snapshot)
        opportunity_edge = abs(raw_edge)
        tradeable_edge = opportunity_edge - spread_cost - uncertainty_penalty - liquidity_penalty
        market_slug = _first_present(market_snapshot, ("market_slug",))

        blocked_reason = _blocked_reason(
            confidence=confidence,
            raw_edge=raw_edge,
            tradeable_edge=tradeable_edge,
            market_slug=market_slug,
            bankroll=bankroll,
            liquidity_score=liquidity_score,
        )
        trade_allowed = blocked_reason is None
        recommended_side = _recommended_side(trade_allowed=trade_allowed, raw_edge=raw_edge)
        kelly_fraction = _kelly_fraction(
            recommended_side=recommended_side,
            model_probability=model_probability,
            market_probability=market_probability,
        )
        fractional_kelly_fraction = kelly_fraction * FRACTIONAL_KELLY_MULTIPLIER
        recommended_size = _recommended_size(
            trade_allowed=trade_allowed,
            bankroll=bankroll,
            fractional_kelly_fraction=fractional_kelly_fraction,
        )
        risk_decision = _risk_decision(trade_allowed, recommended_size, bankroll, confidence, liquidity_score)
        if risk_decision in {"NO_TRADE", "WATCH", "MANUAL_REVIEW"}:
            trade_allowed = False
            recommended_size = 0.0
            if risk_decision in {"NO_TRADE", "MANUAL_REVIEW"}:
                recommended_side = "NONE"
        risk_level = _risk_level(risk_decision)

        return {
            "model_probability": model_probability,
            "market_probability": market_probability,
            "raw_edge": raw_edge,
            "tradeable_edge": tradeable_edge,
            "spread_cost": spread_cost,
            "uncertainty_penalty": uncertainty_penalty,
            "liquidity_penalty": liquidity_penalty,
            "confidence": confidence,
            "liquidity_score": liquidity_score,
            "recommended_side": recommended_side,
            "recommended_size": recommended_size,
            "trade_allowed": trade_allowed,
            "blocked_reason": blocked_reason,
            "risk_decision": risk_decision,
            "risk_level": risk_level,
            "bankroll": bankroll,
            "max_trade_risk_pct": MAX_TRADE_RISK_PCT,
            "max_total_exposure_pct": MAX_TOTAL_EXPOSURE_PCT,
            "current_total_exposure": 0.0,
            "kelly_fraction": kelly_fraction,
            "fractional_kelly_fraction": fractional_kelly_fraction,
            "reason": _reason(trade_allowed, raw_edge, tradeable_edge, recommended_side, blocked_reason),
        }


def _first_present(obj, field_names: tuple[str, ...]):
    for field_name in field_names:
        value = getattr(obj, field_name, None)
        if value is not None:
            return value
    return None


def _probability(value) -> float:
    if value is None:
        return 0.0
    return _clamp(float(value), 0, 1)


def _liquidity_score_and_penalty(market_snapshot) -> tuple[float, float]:
    liquidity = _first_present(market_snapshot, ("liquidity",))
    if liquidity is None:
        score, penalty = 0.2, 0.07
    else:
        liquidity = float(liquidity)
        if liquidity >= 10000:
            score, penalty = 1.0, 0.00
        elif liquidity >= 2500:
            score, penalty = 0.6, 0.02
        else:
            score, penalty = 0.3, 0.05

    if bool(_first_present(market_snapshot, ("order_book_available",))):
        score = min(1.0, score + 0.1)
    return score, penalty


def _blocked_reason(
    confidence: float,
    raw_edge: float,
    tradeable_edge: float,
    market_slug: str | None,
    bankroll: float,
    liquidity_score: float,
) -> str | None:
    if confidence < 0.60:
        return "confidence_below_minimum"
    if abs(raw_edge) < 0.05:
        return "raw_edge_below_minimum"
    if tradeable_edge <= 0:
        return "tradeable_edge_not_positive"
    if not market_slug:
        return "market_slug_missing"
    if bankroll <= 0:
        return "bankroll_not_positive"
    if liquidity_score < 0.25:
        return "liquidity_score_below_minimum"
    return None


def _recommended_side(trade_allowed: bool, raw_edge: float) -> str:
    if not trade_allowed:
        return "NONE"
    if raw_edge > 0:
        return "YES"
    if raw_edge < 0:
        return "NO"
    return "NONE"


def _kelly_fraction(recommended_side: str, model_probability: float, market_probability: float) -> float:
    if recommended_side == "YES":
        return _binary_kelly(p=model_probability, market_probability=market_probability)
    if recommended_side == "NO":
        return _binary_kelly(p=1 - model_probability, market_probability=1 - market_probability)
    return 0.0


def _binary_kelly(p: float, market_probability: float) -> float:
    if market_probability <= 0 or market_probability >= 1:
        return 0.0
    b = (1 / market_probability) - 1
    if b <= 0:
        return 0.0
    return _clamp((b * p - (1 - p)) / b, 0, 1)


def _recommended_size(trade_allowed: bool, bankroll: float, fractional_kelly_fraction: float) -> float:
    if not trade_allowed:
        return 0.0
    return max(0.0, min(bankroll * fractional_kelly_fraction, bankroll * MAX_TRADE_RISK_PCT))


def _risk_decision(
    trade_allowed: bool,
    recommended_size: float,
    bankroll: float,
    confidence: float,
    liquidity_score: float,
) -> str:
    if not trade_allowed:
        return "NO_TRADE"
    if confidence < 0.70 or liquidity_score < 0.6:
        return "WATCH"
    if recommended_size <= bankroll * 0.01:
        return "PAPER_TRADE_SMALL"
    return "PAPER_TRADE_NORMAL"


def _risk_level(risk_decision: str) -> str:
    return {
        "NO_TRADE": "blocked",
        "WATCH": "low",
        "PAPER_TRADE_SMALL": "medium",
        "PAPER_TRADE_NORMAL": "high",
        "MANUAL_REVIEW": "high",
    }[risk_decision]


def _reason(
    trade_allowed: bool,
    raw_edge: float,
    tradeable_edge: float,
    recommended_side: str,
    blocked_reason: str | None,
) -> str:
    if not trade_allowed:
        return f"Risk analysis blocked: {blocked_reason}."
    return (
        f"Risk analysis allows {recommended_side} side with raw edge {raw_edge:.4f} "
        f"and tradeable edge {tradeable_edge:.4f}."
    )


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
