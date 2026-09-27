from __future__ import annotations
from uuid import uuid4
from .models import EvidenceItem, RecommendationContext, RecommendationResult


def _relevant(e: EvidenceItem, ctx: RecommendationContext) -> bool:
    if e.well_id == ctx.well_id and e.source_type != "prediction":
        return False
    if e.event_type and e.event_type != ctx.risk_type:
        return False
    if e.formation and ctx.formation and e.formation != ctx.formation:
        return False
    return True


def generate_recommendation(ctx: RecommendationContext, *, min_evidence: int = 1) -> RecommendationResult:
    """Generate a recommendation only from supplied evidence.

    The engine intentionally avoids inventing operational procedures. With
    insufficient evidence it returns a monitoring/evidence-gap statement rather
    than pretending a procedure is supported.
    """
    if min_evidence < 1:
        raise ValueError("min_evidence must be >= 1")
    evidence = [e for e in ctx.evidence if _relevant(e, ctx)]
    evidence.sort(key=lambda e: e.similarity if e.similarity is not None else 0.0, reverse=True)
    sufficient = len(evidence) >= min_evidence
    priority = "high" if ctx.severity.lower() in {"high", "critical"} or ctx.probability >= 0.75 else "medium"

    if not sufficient:
        return RecommendationResult(
            recommendation_id=f"rec-{uuid4()}",
            well_id=ctx.well_id,
            risk_type=ctx.risk_type,
            priority=priority,
            title="Evidence insufficient for an operational recommendation",
            recommendation=(
                "Evidence is insufficient to support a specific operational procedure. "
                "Review current conditions and retrieve additional historical wells, incidents, or documents before acting."
            ),
            rationale="No sufficiently relevant historical/document evidence was supplied to the recommendation engine.",
            evidence_sufficient=False,
            evidence=[],
            disclaimer="This system does not invent or substitute for approved OIL operating procedures.",
        )

    cited = evidence[:5]
    source_text = "; ".join(
        f"{e.source_type} {e.source_id}" + (f" ({e.similarity:.0%} similarity)" if e.similarity is not None else "")
        for e in cited
    )
    recommendation = (
        f"Review the cited historical evidence for {ctx.risk_type} at the current well and compare the documented conditions "
        f"before selecting an operational response. Relevant evidence: {source_text}."
    )
    return RecommendationResult(
        recommendation_id=f"rec-{uuid4()}",
        well_id=ctx.well_id,
        risk_type=ctx.risk_type,
        priority=priority,
        title=f"Evidence review for {ctx.risk_type.replace('_', ' ')} risk",
        recommendation=recommendation,
        rationale=(
            f"The recommendation is grounded in {len(cited)} supplied historical/document/prediction evidence item(s). "
            "The engine does not infer an unverified field procedure."
        ),
        evidence_sufficient=True,
        evidence=cited,
        disclaimer="Historical similarity is supporting evidence, not proof that the same operational response is appropriate now. Follow approved OIL procedures and engineering judgement.",
    )
