from nwis_decision_support import RecommendationContext, EvidenceItem, generate_recommendation

def test_recommendation_cites_evidence():
    ctx = RecommendationContext(
        well_id="W-001", risk_type="mud_loss", probability=.78, severity="high",
        evidence=[EvidenceItem(source_id="EV-2", source_type="historical_event", well_id="W-002", event_type="mud_loss", similarity=.91, summary="Historical mud-loss event.")],
    )
    result = generate_recommendation(ctx)
    assert result.evidence_sufficient is True
    assert result.evidence[0].source_id == "EV-2"
    assert "EV-2" in result.recommendation

def test_insufficient_evidence_is_explicit():
    ctx = RecommendationContext(well_id="W-001", risk_type="kick", probability=.8, severity="high")
    result = generate_recommendation(ctx)
    assert result.evidence_sufficient is False
    assert "insufficient" in result.recommendation.lower()
