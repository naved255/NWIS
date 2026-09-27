"""Thin Qdrant adapter; no RAG or embedding generation is performed here."""
from __future__ import annotations
from typing import Any, Iterable
from uuid import UUID
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue
from ..config import get_settings
from ..schemas import QdrantChunkPayload


class QdrantVectorStore:
    """Stores externally generated embeddings and chunk metadata in Qdrant."""

    def __init__(self, client: QdrantClient, collection: str):
        self.client = client
        self.collection = collection

    @classmethod
    def from_settings(cls) -> "QdrantVectorStore":
        settings = get_settings()
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
        return cls(client, settings.qdrant_collection)

    def ensure_collection(self, vector_size: int, distance: Distance = Distance.COSINE) -> None:
        """Create the collection if it does not exist."""
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )

    def upsert_chunks(self, points: Iterable[tuple[str | int | UUID, list[float], QdrantChunkPayload]]) -> None:
        """Upsert precomputed embeddings and payloads for document chunks."""
        records = []
        for point_id, vector, payload in points:
            records.append(PointStruct(id=str(point_id), vector=vector, payload=payload.model_dump()))
        if records:
            self.client.upsert(collection_name=self.collection, points=records, wait=True)

    def delete_chunk(self, point_id: str | int | UUID) -> None:
        """Delete one embedding point."""
        self.client.delete(collection_name=self.collection, points_selector=[str(point_id)], wait=True)

    def search_by_well(self, well_id: str, query_vector: list[float], limit: int = 10) -> list[Any]:
        """Similarity search constrained to a well ID."""
        query_filter = Filter(must=[FieldCondition(key="well_id", match=MatchValue(value=well_id))])
        return self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        ).points

    def search(self, query_vector: list[float], limit: int = 10, well_id: str | None = None, document_type: str | None = None, event_type: str | None = None) -> list[Any]:
        """Similarity search with optional metadata filters."""
        conditions = []
        for key, value in (("well_id", well_id), ("document_type", document_type), ("event_type", event_type)):
            if value is not None:
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        query_filter = Filter(must=conditions) if conditions else None
        return self.client.query_points(collection_name=self.collection, query=query_vector, query_filter=query_filter, limit=limit, with_payload=True).points
