"""
embedder.py — Generates text embeddings for document chunks.

Uses OpenAI text-embedding-3-small (1536-dim) by default.
Batches requests for efficiency.
"""
from __future__ import annotations

import time
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings
from src.logger import get_logger
from src.models import DocumentChunk

logger = get_logger(__name__)
settings = get_settings()

_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        import openai
        _openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    return _openai_client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    Batches up to 100 texts per API call.
    """
    if not texts:
        return []

    client = _get_openai_client()
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # Clean text — remove null chars
        batch = [t.replace("\x00", " ").strip() or " " for t in batch]

        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        logger.debug(f"Embedded batch {i // batch_size + 1} ({len(batch)} texts)")

    return all_embeddings


def embed_chunks(chunks: list[DocumentChunk]) -> tuple[list[DocumentChunk], list[list[float]]]:
    """
    Embed a list of DocumentChunks and return them paired with their embeddings.
    """
    if not chunks:
        return [], []

    texts = [chunk.content for chunk in chunks]
    logger.info(f"Generating embeddings for {len(texts)} chunks…")
    start = time.time()
    embeddings = embed_texts(texts)
    elapsed = time.time() - start
    logger.info(f"✓ Embedded {len(embeddings)} chunks in {elapsed:.2f}s")
    return chunks, embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    results = embed_texts([query])
    return results[0]
