from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from .models import AlertContext, AlertResult, AlertRule

DEFAULT_RULES = [
    AlertRule(
        name="high_risk_with_historical_match",
        min_probability=0.75,
        require_historical_match=True,
        min_historical_similarity=0.70,
        require_depth_in_interval=True,
        output_severity="high",
    ),
    AlertRule(
        name="high_probability_anomalous_parameters",
        min_probability=0.85,
        require_parameter_anomaly=True,
        output_severity="critical",
    ),
]


def _depth_matches(ctx: AlertContext, tolerance: float) -> bool:
    if ctx.depth_m is None or ctx.risk_interval_start_m is None or ctx.risk_interval_end_m is None:
        return False
    lo, hi = sorted((ctx.risk_interval_start_m, ctx.risk_interval_end_m))
    return lo - tolerance <= ctx.depth_m <= hi + tolerance


def _rule_matches(ctx: AlertContext, rule: AlertRule) -> bool:
    if not rule.enabled:
        return False
    if rule.min_probability is not None and ctx.probability < rule.min_probability:
        return False
    if rule.severities is not None and ctx.severity not in rule.severities:
        return False
    if rule.formation and ctx.formation != rule.formation:
        return False
    if rule.require_historical_match:
        matches = [e for e in ctx.historical_evidence if (rule.min_historical_similarity is None or e.similarity >= rule.min_historical_similarity)]
        if not matches:
            return False
    if rule.require_depth_in_interval and not _depth_matches(ctx, rule.depth_tolerance_m):
        return False
    if rule.require_parameter_anomaly and not any(a.is_anomalous for a in ctx.parameter_anomalies):
        return False
    return True


def generate_alert(ctx: AlertContext, rules: list[AlertRule] | None = None) -> AlertResult:
    """Evaluate configurable rules and return a structured alert if one fires.

    No alert is generated when no supplied rule matches. Evidence is copied from
    the caller and is never fabricated by this engine.
    """
    rules = rules if rules is not None else DEFAULT_RULES
    for rule in rules:
        if not _rule_matches(ctx, rule):
            continue
        evidence = sorted(ctx.historical_evidence, key=lambda e: e.similarity, reverse=True)
        reasons = [f"ML probability is {ctx.probability:.0%}"]
        if evidence:
            reasons.append(f"historical {ctx.risk_type} evidence matches at up to {evidence[0].similarity:.0%} similarity")
        if ctx.depth_m is not None and _depth_matches(ctx, rule.depth_tolerance_m):
            reasons.append("active depth is within the configured risk interval")
        anomalies = [a.parameter for a in ctx.parameter_anomalies if a.is_anomalous]
        if anomalies:
            reasons.append("real-time anomalies: " + ", ".join(anomalies))
        return AlertResult(
            alert_id=f"alert-{uuid4()}",
            generated=True,
            well_id=ctx.well_id,
            risk_type=ctx.risk_type,
            severity=rule.output_severity,
            probability=ctx.probability,
            depth_m=ctx.depth_m,
            reason="; ".join(reasons) + ".",
            evidence=evidence,
            timestamp=ctx.timestamp,
            recommended_action=ctx.recommended_action,
            rule_name=rule.name,
        )
    return AlertResult(
        generated=False,
        well_id=ctx.well_id,
        risk_type=ctx.risk_type,
        probability=ctx.probability,
        depth_m=ctx.depth_m,
        timestamp=ctx.timestamp,
    )
