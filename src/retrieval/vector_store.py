"""
vector_store.py — ChromaDB wrapper for storing and retrieving document embeddings.

Uses persistent storage so the index survives restarts.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config import get_settings
from src.logger import get_logger
from src.models import ChunkType, DocumentChunk, RetrievedChunk

logger = get_logger(__name__)
settings = get_settings()


class VectorStore:
    """ChromaDB-backed vector store for multimodal document chunks."""

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"VectorStore ready — collection '{settings.chroma_collection_name}' "
            f"({self._collection.count()} docs)"
        )

    # ─── Write ────────────────────────────────────────────────────────────────

    def upsert(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """Upsert chunks and their embeddings into ChromaDB."""
        if not chunks:
            return

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "doc_id": chunk.doc_id,
                "doc_name": chunk.doc_name,
                "doc_type": chunk.doc_type.value,
                "chunk_type": chunk.chunk_type.value,
                "page_number": chunk.page_number or -1,
                "image_index": chunk.image_index if chunk.image_index is not None else -1,
                **{k: str(v) for k, v in chunk.metadata.items()},
            }
            for chunk in chunks
        ]

        # Batch upserts (ChromaDB limit ~5000 per call)
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            self._collection.upsert(
                ids=ids[i : i + batch_size],
                embeddings=embeddings[i : i + batch_size],
                documents=documents[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

        logger.debug(f"Upserted {len(chunks)} chunks")

    def delete_document(self, doc_id: str) -> int:
        """Delete all chunks for a given document."""
        results = self._collection.get(where={"doc_id": doc_id})
        ids = results.get("ids", [])
        if ids:
            self._collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} chunks for doc_id={doc_id}")
        return len(ids)

    # ─── Read ─────────────────────────────────────────────────────────────────

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve the top-k most similar chunks.

        Args:
            query_embedding: Query vector
            top_k: Number of results
            where: Optional ChromaDB filter dict

        Returns:
            List of RetrievedChunk sorted by similarity (highest first)
        """
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, max(self._collection.count(), 1)),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        retrieved = []
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for chunk_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
            # ChromaDB cosine distance → similarity score
            score = 1.0 - dist

            if score < settings.similarity_threshold:
                continue

            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    doc_id=meta.get("doc_id", ""),
                    doc_name=meta.get("doc_name", ""),
                    chunk_type=ChunkType(meta.get("chunk_type", "text")),
                    content=doc,
                    score=round(score, 4),
                    page_number=meta.get("page_number") if meta.get("page_number", -1) != -1 else None,
                    image_index=meta.get("image_index") if meta.get("image_index", -1) != -1 else None,
                    metadata=meta,
                )
            )

        return sorted(retrieved, key=lambda x: x.score, reverse=True)

    def count(self) -> int:
        return self._collection.count()

    def list_documents(self) -> list[dict[str, Any]]:
        """Return unique documents stored in the vector store."""
        results = self._collection.get(include=["metadatas"])
        seen: dict[str, dict] = {}
        for meta in results.get("metadatas", []):
            doc_id = meta.get("doc_id", "")
            if doc_id not in seen:
                seen[doc_id] = {
                    "doc_id": doc_id,
                    "doc_name": meta.get("doc_name", ""),
                    "doc_type": meta.get("doc_type", ""),
                }
        return list(seen.values())

    def reset(self) -> None:
        """⚠️  Delete all data in the collection."""
        self._client.delete_collection(settings.chroma_collection_name)
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning("Vector store reset — all data deleted")


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """Singleton vector store instance."""
    return VectorStore()
