from nwis_rag.answerer import EvidenceAnswerer, INSUFFICIENT
from nwis_rag.schemas import EvidenceItem


def evidence(text="Mud losses occurred at 2920 m."):
    return [
        EvidenceItem(
            evidence_id="chunk-1",
            text=text,
            score=0.91,
            source_uri="s3://nwis/ddr-1.pdf",
            source_name="DDR-1.pdf",
            page=12,
            metadata={"well_id": "W-1", "depth": 2920},
        )
    ]


def test_insufficient_evidence_message():
    result = EvidenceAnswerer().answer("What happened?", [])
    assert result.sufficient_evidence is False
    assert result.message == INSUFFICIENT


def test_sources_are_always_returned():
    result = EvidenceAnswerer().answer("What happened?", evidence())
    assert result.sufficient_evidence is True
    assert result.source
    assert "DDR-1.pdf" in result.source[0]
    assert result.fact == ["Mud losses occurred at 2920 m."]


def test_llm_output_cannot_remove_actual_sources():
    answerer = EvidenceAnswerer(llm=lambda _: "FACT:\n- Supported fact\nINFERENCE:\n- None")
    result = answerer.answer("What happened?", evidence())
    assert result.fact == ["Supported fact"]
    assert result.source[0].startswith("[chunk-1]")
