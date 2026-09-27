"""Chunking and indexing utilities for document-processing outputs."""

from __future__ import annotations

from typing import Iterable

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import RAGSettings
from .schemas import ChunkRecord
from .vector_store import QdrantKnowledgeStore


def split_chunk_record(
    record: ChunkRecord,
    settings: RAGSettings | None = None,
) -> list[ChunkRecord]:
    """Split one extracted document record while preserving source metadata."""
    settings = settings or RAGSettings.from_env()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    texts = splitter.split_text(record.text)
    if not texts:
        return []
    result: list[ChunkRecord] = []
    for index, text in enumerate(texts):
        result.append(
            record.model_copy(
                update={
                    "chunk_id": f"{record.chunk_id}:{index}",
                    "text": text,
                }
            )
        )
    return result


def index_chunks(
    records: Iterable[ChunkRecord],
    store: QdrantKnowledgeStore,
    settings: RAGSettings | None = None,
) -> list[str]:
    """Split extracted records and index them in Qdrant."""
    chunks: list[ChunkRecord] = []
    for record in records:
        chunks.extend(split_chunk_record(record, settings))
    return store.add_chunks(chunks)
