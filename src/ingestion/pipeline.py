"""
pipeline.py — End-to-end ingestion pipeline.

Flow:
  File → DocumentProcessor → [text chunks]
                           → [images] → ImageCaptioner → [caption chunks]
  All chunks → Embedder → VectorStore
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path

from src.config import get_settings
from src.ingestion.document_processor import process_document
from src.ingestion.embedder import embed_chunks
from src.ingestion.image_captioner import caption_images_to_chunks
from src.logger import get_logger
from src.models import IngestedDocument
from src.retrieval.vector_store import get_vector_store

logger = get_logger(__name__)
settings = get_settings()


def ingest_document(file_path: str | Path) -> IngestedDocument:
    """
    Full ingestion pipeline for a single document.

    Steps:
    1. Extract text chunks and raw images
    2. Caption images via Vision LLM
    3. Combine all chunks
    4. Generate embeddings
    5. Upsert into vector store

    Returns an IngestedDocument summary.
    """
    file_path = Path(file_path)
    start = time.time()

    logger.info(f"━━━ Ingesting: {file_path.name} ━━━")

    # ── Step 1: Extract ────────────────────────────────────────────────────────
    text_chunks, images, doc_id, doc_type = process_document(file_path)
    logger.info(f"  Extracted {len(text_chunks)} text chunks, {len(images)} images")

    # ── Step 2: Caption Images ─────────────────────────────────────────────────
    image_chunks = []
    if images:
        image_chunks = caption_images_to_chunks(
            images=images,
            doc_id=doc_id,
            doc_name=file_path.name,
            doc_type=doc_type,
        )
        logger.info(f"  Generated {len(image_chunks)} image caption chunks")

    # ── Step 3: Combine ────────────────────────────────────────────────────────
    all_chunks = text_chunks + image_chunks
    if not all_chunks:
        raise ValueError(f"No content extracted from {file_path.name}")

    # ── Step 4: Embed ──────────────────────────────────────────────────────────
    chunks, embeddings = embed_chunks(all_chunks)

    # ── Step 5: Store ──────────────────────────────────────────────────────────
    vector_store = get_vector_store()
    vector_store.upsert(chunks, embeddings)
    logger.info(f"  ✓ Stored {len(chunks)} chunks in vector store")

    elapsed = time.time() - start
    result = IngestedDocument(
        doc_id=doc_id,
        doc_name=file_path.name,
        doc_type=doc_type,
        total_chunks=len(all_chunks),
        text_chunks=len(text_chunks),
        image_chunks=len(image_chunks),
        processing_time_sec=round(elapsed, 2),
    )
    logger.info(f"━━━ Done: {file_path.name} in {elapsed:.2f}s ━━━")
    return result


def ingest_directory(dir_path: str | Path) -> list[IngestedDocument]:
    """Ingest all supported files in a directory."""
    dir_path = Path(dir_path)
    supported = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".md", ".docx"}
    files = [f for f in dir_path.iterdir() if f.suffix.lower() in supported]

    if not files:
        logger.warning(f"No supported files found in {dir_path}")
        return []

    results = []
    for f in files:
        try:
            result = ingest_document(f)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to ingest {f.name}: {e}")

    return results
