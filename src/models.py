"""
models.py — Shared Pydantic models used across ingestion, retrieval, and generation.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    DOCX = "docx"
    UNKNOWN = "unknown"


class ChunkType(str, Enum):
    TEXT = "text"
    IMAGE_CAPTION = "image_caption"
    TABLE = "table"


# ─── Ingestion Models ──────────────────────────────────────────────────────────

class ImageData(BaseModel):
    """Represents an extracted image with its generated caption."""
    image_index: int
    page_number: int | None = None
    base64_data: str
    caption: str = ""
    width: int = 0
    height: int = 0
    format: str = "PNG"


class DocumentChunk(BaseModel):
    """A single chunk of content (text or image caption) ready for embedding."""
    chunk_id: str
    doc_id: str
    doc_name: str
    doc_type: DocumentType
    chunk_type: ChunkType
    content: str
    page_number: int | None = None
    image_index: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IngestedDocument(BaseModel):
    """Result of processing a document through the ingestion pipeline."""
    doc_id: str
    doc_name: str
    doc_type: DocumentType
    total_chunks: int
    text_chunks: int
    image_chunks: int
    processing_time_sec: float
    metadata: dict[str, Any] = Field(default_factory=dict)


# ─── Retrieval Models ──────────────────────────────────────────────────────────

class RetrievedChunk(BaseModel):
    """A chunk returned from vector similarity search."""
    chunk_id: str
    doc_id: str
    doc_name: str
    chunk_type: ChunkType
    content: str
    score: float
    page_number: int | None = None
    image_index: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ─── Generation Models ─────────────────────────────────────────────────────────

class Citation(BaseModel):
    """A source citation included in the answer."""
    doc_name: str
    chunk_type: ChunkType
    page_number: int | None = None
    relevance_score: float


class RAGResponse(BaseModel):
    """Final response from the RAG pipeline."""
    query: str
    answer: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    model_used: str
    processing_time_sec: float


# ─── API Models ───────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    include_images: bool = True


class HealthResponse(BaseModel):
    status: str
    version: str
    vector_store_docs: int
    llm_provider: str
