"""Qdrant adapter used by the NWIS RAG service."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from .config import RAGSettings
from .embeddings import build_embeddings
from .filters import build_qdrant_filter
from .schemas import ChunkRecord, EvidenceItem, RetrievalFilters


class QdrantKnowledgeStore:
    """Small adapter around LangChain's QdrantVectorStore.

    The rest of NWIS does not need to know how Qdrant is configured.
    """

    def __init__(self, settings: RAGSettings | None = None) -> None:
        self.settings = settings or RAGSettings.from_env()
        self.client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
        )
        self.embeddings = build_embeddings(self.settings)
        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=self.settings.qdrant_collection,
            embedding=self.embeddings,
        )

    def add_chunks(self, chunks: list[ChunkRecord]) -> list[str]:
        """Embed and upsert chunks into Qdrant, returning chunk IDs."""
        if not chunks:
            return []
        documents = [
            Document(
                page_content=chunk.text,
                metadata=self._metadata(chunk),
            )
            for chunk in chunks
        ]
        ids = [chunk.chunk_id for chunk in chunks]
        self.store.add_documents(documents=documents, ids=ids)
        return ids

    def similarity_search(
        self,
        query: str,
        *,
        filters: RetrievalFilters | None = None,
        k: int = 8,
        score_threshold: float | None = None,
    ) -> list[EvidenceItem]:
        """Run semantic search and convert results into traceable evidence."""
        qfilter = build_qdrant_filter(filters or RetrievalFilters())
        pairs = self.store.similarity_search_with_score(
            query,
            k=k,
            filter=qfilter,
            score_threshold=score_threshold,
        )
        return [self._to_evidence(doc, score) for doc, score in pairs]

    def _metadata(self, chunk: ChunkRecord) -> dict[str, Any]:
        """Convert a chunk into Qdrant-safe payload metadata."""
        metadata: dict[str, Any] = {
            "chunk_id": chunk.chunk_id,
            "source_uri": chunk.source_uri,
            "source_name": chunk.source_name,
        }
        optional = {
            "well_id": chunk.well_id,
            "formation": chunk.formation,
            "depth": chunk.depth,
            "depth_top": chunk.depth_top,
            "depth_bottom": chunk.depth_bottom,
            "event_type": chunk.event_type,
            "document_type": chunk.document_type,
            "date": datetime.combine(chunk.date, time.min) if chunk.date else None,
            "location": chunk.location,
            "page": chunk.page,
        }
        metadata.update({k: v for k, v in optional.items() if v is not None})
        metadata.update(chunk.extra_metadata)
        return metadata

    @staticmethod
    def _to_evidence(document: Document, score: float) -> EvidenceItem:
        """Convert a LangChain document result into an evidence contract."""
        metadata = dict(document.metadata)
        source_uri = str(metadata.get("source_uri", "unknown"))
        source_name = str(metadata.get("source_name", source_uri))
        page = metadata.get("page")
        return EvidenceItem(
            evidence_id=str(metadata.get("chunk_id", metadata.get("id", "unknown"))),
            text=document.page_content,
            score=float(score),
            source_uri=source_uri,
            source_name=source_name,
            page=int(page) if page is not None else None,
            metadata=metadata,
        )
