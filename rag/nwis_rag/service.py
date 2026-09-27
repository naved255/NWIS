"""Public RAG service API for NWIS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from .answerer import EvidenceAnswerer, INSUFFICIENT
from .config import RAGSettings
from .schemas import AnswerResponse, EvidenceItem, RetrievalFilters, RetrievalQuery, RetrievalResponse
if TYPE_CHECKING:
    from .vector_store import QdrantKnowledgeStore


class KnowledgeStore(Protocol):
    """Interface implemented by the Qdrant adapter or test doubles."""

    def similarity_search(
        self,
        query: str,
        *,
        filters: RetrievalFilters | None = None,
        k: int = 8,
        score_threshold: float | None = None,
    ) -> list[EvidenceItem]: ...


class RAGService:
    """Historical drilling retrieval service exposed to other NWIS modules."""

    def __init__(
        self,
        store: KnowledgeStore | None = None,
        answerer: EvidenceAnswerer | None = None,
        settings: RAGSettings | None = None,
    ) -> None:
        self.settings = settings or RAGSettings.from_env()
        if store is not None:
            self.store = store
        else:
            from .vector_store import QdrantKnowledgeStore
            self.store = QdrantKnowledgeStore(self.settings)
        self.answerer = answerer or EvidenceAnswerer()

    def retrieve_similar_documents(
        self,
        query: str,
        *,
        filters: RetrievalFilters | None = None,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> RetrievalResponse:
        """Retrieve semantically similar historical document chunks."""
        request = RetrievalQuery(
            query=query,
            filters=filters or RetrievalFilters(),
            top_k=top_k or self.settings.top_k,
            score_threshold=score_threshold if score_threshold is not None else self.settings.score_threshold,
        )
        evidence = self.store.similarity_search(
            request.query,
            filters=request.filters,
            k=request.top_k,
            score_threshold=request.score_threshold,
        )
        return self._retrieval_response(query, evidence)

    def retrieve_similar_events(
        self,
        query: str,
        *,
        event_type: str | None = None,
        filters: RetrievalFilters | None = None,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> RetrievalResponse:
        """Retrieve historical event evidence, optionally constrained by event type."""
        merged = filters or RetrievalFilters()
        if event_type is not None:
            merged = merged.model_copy(update={"event_type": event_type})
        return self.retrieve_similar_documents(
            query,
            filters=merged,
            top_k=top_k,
            score_threshold=score_threshold,
        )

    def retrieve_offset_well_knowledge(
        self,
        query: str,
        *,
        location: str | None = None,
        target_well_id: str | None = None,
        filters: RetrievalFilters | None = None,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> RetrievalResponse:
        """Retrieve historical knowledge constrained to an offset-well location.

        ``location`` is treated as a normalized metadata key produced by the
        geo/data-ingestion modules. This method does not calculate geographic
        distance itself; that belongs to the geo module.
        """
        merged = filters or RetrievalFilters()
        updates = {}
        if location is not None:
            updates["location"] = location
        if updates:
            merged = merged.model_copy(update=updates)
        evidence = self.retrieve_similar_documents(
            query,
            filters=merged,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        if target_well_id and evidence.evidence:
            # The geo module may supply already-selected offset wells. This
            # optional guard prevents direct target-well evidence when payload
            # contains a well_id, without assuming every chunk has one.
            evidence.evidence = [
                item for item in evidence.evidence
                if item.metadata.get("well_id") != target_well_id
            ]
            evidence.sufficient_evidence = bool(evidence.evidence)
            if not evidence.sufficient_evidence:
                evidence.message = INSUFFICIENT
        return evidence

    def answer_question(
        self,
        question: str,
        *,
        filters: RetrievalFilters | None = None,
        top_k: int | None = None,
        score_threshold: float | None = None,
    ) -> AnswerResponse:
        """Retrieve evidence and produce an explicitly structured answer."""
        result = self.retrieve_similar_documents(
            question,
            filters=filters,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        return self.answerer.answer(question, result.evidence)

    @staticmethod
    def _retrieval_response(query: str, evidence: list[EvidenceItem]) -> RetrievalResponse:
        sufficient = bool(evidence)
        return RetrievalResponse(
            query=query,
            evidence=evidence,
            sufficient_evidence=sufficient,
            message=None if sufficient else INSUFFICIENT,
        )
