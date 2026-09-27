"""Sentence Transformer embeddings exposed through LangChain."""

from __future__ import annotations

from langchain_huggingface import HuggingFaceEmbeddings

from .config import RAGSettings


def build_embeddings(settings: RAGSettings | None = None) -> HuggingFaceEmbeddings:
    """Create the configured Sentence Transformers embedding model."""
    settings = settings or RAGSettings.from_env()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )
