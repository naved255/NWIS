"""Configuration for the NWIS RAG service."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RAGSettings:
    """Runtime settings loaded from environment variables."""

    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY") or None
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "nwis_drilling_knowledge")
    embedding_model: str = os.getenv(
        "RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    embedding_device: str = os.getenv("RAG_EMBEDDING_DEVICE", "cpu")
    top_k: int = int(os.getenv("RAG_TOP_K", "8"))
    score_threshold: float = float(os.getenv("RAG_SCORE_THRESHOLD", "0.20"))
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))

    @classmethod
    def from_env(cls) -> "RAGSettings":
        """Create settings from the current environment."""
        return cls(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
            qdrant_collection=os.getenv("QDRANT_COLLECTION", "nwis_drilling_knowledge"),
            embedding_model=os.getenv(
                "RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            embedding_device=os.getenv("RAG_EMBEDDING_DEVICE", "cpu"),
            top_k=int(os.getenv("RAG_TOP_K", "8")),
            score_threshold=float(os.getenv("RAG_SCORE_THRESHOLD", "0.20")),
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "1200")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "150")),
        )
