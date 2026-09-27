from nlp_extraction import DrillingNLPExtractor
from nlp_extraction.models import DocumentInput, DocumentPage, EventType, Severity

SAMPLE = """
Well Name: OIL-X-101. Date: 12/08/2025.
At 2840 m severe mud loss occurred while drilling through the Barail Formation.
The crew pumped 20 bbl LCM and reduced the flow rate to control the losses.
At 2910 m a kick was detected after an increase in flow; the well was shut in.
The BHA included MWD and a PDC bit. ROP was 28 m/hr, WOB 18 klbf and RPM 120.
Casing 9.625 in was run at 3050 m. A cementing problem occurred with poor returns.
Lesson learned: monitor flow closely before increasing pump rate.
""".strip()


def make_document():
    return DocumentInput(document_id="DOC-001", pages=[DocumentPage(page_number=3, text=SAMPLE)])


def test_contextual_event_extraction():
    result = DrillingNLPExtractor().extract(make_document())
    loss = next(e for e in result.events if e.event_type == EventType.MUD_LOSS)
    assert loss.depth_m == 2840
    assert loss.severity == Severity.HIGH
    assert loss.provenance.document_id == "DOC-001"
    assert loss.provenance.page_number == 3
    assert "severe mud loss" in loss.provenance.source_text.lower()


def test_other_events_and_provenance():
    result = DrillingNLPExtractor().extract(make_document())
    types = {e.event_type for e in result.events}
    assert EventType.KICK in types
    assert EventType.CEMENTING_PROBLEM in types
    assert all(e.provenance.source_text for e in result.events)


def test_entities_and_parameters():
    result = DrillingNLPExtractor().extract(make_document())
    values = {(e.entity_type, e.value) for e in result.entities}
    assert ("WELL", "OIL-X-101") in values
    assert any(e.metadata.get("parameter") == "ROP" for e in result.entities)
    assert any(e.metadata.get("parameter") == "WOB" for e in result.entities)
    assert any(e.entity_type == "EQUIPMENT" and e.value.upper() == "MWD" for e in result.entities)


def test_mitigation_and_lesson():
    result = DrillingNLPExtractor().extract(make_document())
    assert any("LCM" in a.action for a in result.mitigation_actions)
    assert any(a.is_recommendation for a in result.mitigation_actions)
    assert any("monitor flow" in l.lesson.lower() for l in result.lessons_learned)


def test_bare_mention_is_not_always_an_event():
    doc = DocumentInput(document_id="DOC-002", pages=[DocumentPage(
        page_number=1,
        text="Fishing tools were available in the warehouse. The casing program listed 9.625 in casing."
    )])
    result = DrillingNLPExtractor().extract(doc)
    assert not any(e.event_type == EventType.FISHING for e in result.events)
    assert not any(e.event_type == EventType.CASING_EVENT for e in result.events)


def test_depth_casing_and_mud_program_entities():
    doc = DocumentInput(document_id="DOC-003", pages=[DocumentPage(
        page_number=2,
        text="At 2500 m the WBM mud program used 10.2 ppg mud. 9.625 in casing was run."
    )])
    result = DrillingNLPExtractor().extract(doc)
    assert any(e.entity_type == "DEPTH" and e.metadata.get("depth_m") == 2500 for e in result.entities)
    assert any(e.entity_type == "CASING" and e.metadata.get("size_in") == 9.625 for e in result.entities)
    assert any(e.entity_type == "MUD_PROGRAM" for e in result.entities)
