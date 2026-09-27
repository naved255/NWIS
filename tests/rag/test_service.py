from nwis_rag.schemas import EvidenceItem, RetrievalFilters
from nwis_rag.service import RAGService


class FakeStore:
    def __init__(self):
        self.calls = []

    def similarity_search(self, query, *, filters=None, k=8, score_threshold=None):
        self.calls.append((query, filters, k, score_threshold))
        return [
            EvidenceItem(
                evidence_id="e1",
                text="Stuck pipe was reported.",
                score=0.8,
                source_uri="file:///ddr.pdf",
                source_name="ddr.pdf",
                metadata={"well_id": "OFFSET-1"},
            )
        ]


def test_retrieve_similar_events_sets_event_filter():
    store = FakeStore()
    service = RAGService(store=store)
    result = service.retrieve_similar_events("stuck pipe", event_type="stuck_pipe")
    assert result.sufficient_evidence
    assert store.calls[0][1].event_type == "stuck_pipe"


def test_offset_well_excludes_target_well():
    class MixedStore(FakeStore):
        def similarity_search(self, query, *, filters=None, k=8, score_threshold=None):
            return [
                EvidenceItem(
                    evidence_id="target",
                    text="target evidence",
                    score=0.9,
                    source_uri="target.pdf",
                    source_name="target.pdf",
                    metadata={"well_id": "TARGET"},
                ),
                EvidenceItem(
                    evidence_id="offset",
                    text="offset evidence",
                    score=0.8,
                    source_uri="offset.pdf",
                    source_name="offset.pdf",
                    metadata={"well_id": "OFFSET"},
                ),
            ]

    result = RAGService(store=MixedStore()).retrieve_offset_well_knowledge(
        "mud loss", target_well_id="TARGET"
    )
    assert [e.evidence_id for e in result.evidence] == ["offset"]


def test_answer_question_uses_filters():
    store = FakeStore()
    service = RAGService(store=store)
    result = service.answer_question(
        "What happened near 2900 m?",
        filters=RetrievalFilters(depth_min=2800, depth_max=3000),
    )
    assert result.sufficient_evidence
    assert store.calls[0][1].depth_min == 2800
