"""
retriever.py — Retrieval layer: embeds a query and fetches relevant chunks.
"""
from __future__ import annotations

from src.ingestion.embedder import embed_query
from src.logger import get_logger
from src.models import RetrievedChunk
from src.retrieval.vector_store import get_vector_store

logger = get_logger(__name__)


def retrieve(
    query: str,
    top_k: int = 5,
    include_images: bool = True,
) -> list[RetrievedChunk]:
    """
    Retrieve top-k relevant chunks for a query.

    Args:
        query: User's natural language query
        top_k: Number of chunks to return
        include_images: If False, filter out image-caption chunks

    Returns:
        Sorted list of RetrievedChunk (highest similarity first)
    """
    logger.info(f"Retrieving for query: '{query[:80]}…'")

    query_embedding = embed_query(query)
    vector_store = get_vector_store()

    where = None
    if not include_images:
        where = {"chunk_type": {"$eq": "text"}}

    chunks = vector_store.query(
        query_embedding=query_embedding,
        top_k=top_k,
        where=where,
    )

    logger.info(
        f"  Retrieved {len(chunks)} chunks "
        f"(scores: {[round(c.score, 3) for c in chunks]})"
    )
    return chunks
