"""
test_retrieval_generation.py — Tests for retrieval and generation layers.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.models import ChunkType, Citation, RAGResponse, RetrievedChunk


def _make_chunk(i: int, score: float = 0.9, chunk_type: ChunkType = ChunkType.TEXT) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=f"chunk_{i}",
        doc_id=f"doc_{i}",
        doc_name=f"document_{i}.pdf",
        chunk_type=chunk_type,
        content=f"This is the content of chunk number {i}. It contains useful information.",
        score=score,
        page_number=i,
    )


# ─── Context Building ─────────────────────────────────────────────────────────

class TestContextBuilding:
    def test_build_context_text_chunk(self):
        from src.generation.generator import _build_context
        chunks = [_make_chunk(1)]
        ctx = _build_context(chunks)
        assert "document_1.pdf" in ctx
        assert "chunk number 1" in ctx

    def test_build_context_image_chunk(self):
        from src.generation.generator import _build_context
        chunks = [_make_chunk(1, chunk_type=ChunkType.IMAGE_CAPTION)]
        ctx = _build_context(chunks)
        assert "[IMAGE]" in ctx

    def test_build_context_multiple_chunks(self):
        from src.generation.generator import _build_context
        chunks = [_make_chunk(i) for i in range(3)]
        ctx = _build_context(chunks)
        assert "Source 1" in ctx
        assert "Source 2" in ctx
        assert "Source 3" in ctx


# ─── Generation (mocked LLM) ──────────────────────────────────────────────────

class TestGeneration:
    @patch("src.generation.generator._generate_openai")
    @patch("src.generation.generator.settings")
    def test_generate_returns_rag_response(self, mock_settings, mock_gen):
        from src.generation.generator import generate

        mock_settings.llm_provider = "openai"
        mock_settings.llm_model = "gpt-4o"
        mock_gen.return_value = "Here is the answer based on the documents."

        chunks = [_make_chunk(1), _make_chunk(2)]
        response = generate("What is the main topic?", chunks)

        assert isinstance(response, RAGResponse)
        assert response.answer == "Here is the answer based on the documents."
        assert len(response.citations) == 2
        assert response.model_used == "gpt-4o"

    @patch("src.generation.generator.settings")
    def test_generate_empty_chunks(self, mock_settings):
        from src.generation.generator import generate

        mock_settings.llm_provider = "openai"
        mock_settings.llm_model = "gpt-4o"

        response = generate("What is the main topic?", [])
        assert "couldn't find" in response.answer.lower()
        assert response.citations == []


# ─── Vector Store (in-memory for tests) ───────────────────────────────────────

class TestVectorStore:
    def test_upsert_and_query(self, tmp_path):
        """Integration test using an ephemeral ChromaDB."""
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        from src.models import DocumentChunk, DocumentType

        client = chromadb.PersistentClient(
            path=str(tmp_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        collection = client.get_or_create_collection(
            name="test", metadata={"hnsw:space": "cosine"}
        )

        # Insert a fake chunk with a fake embedding
        chunk = DocumentChunk(
            chunk_id="test_chunk_001",
            doc_id="doc_001",
            doc_name="test.pdf",
            doc_type=DocumentType.PDF,
            chunk_type=ChunkType.TEXT,
            content="Python is a programming language.",
            page_number=1,
        )
        embedding = [0.1] * 1536

        collection.upsert(
            ids=[chunk.chunk_id],
            embeddings=[embedding],
            documents=[chunk.content],
            metadatas=[{"doc_id": chunk.doc_id, "doc_name": chunk.doc_name,
                        "doc_type": chunk.doc_type.value, "chunk_type": chunk.chunk_type.value,
                        "page_number": 1, "image_index": -1}],
        )

        assert collection.count() == 1

        # Query with same embedding should return the chunk
        results = collection.query(
            query_embeddings=[embedding],
            n_results=1,
            include=["documents", "metadatas", "distances"],
        )
        assert len(results["ids"][0]) == 1
        assert results["documents"][0][0] == "Python is a programming language."
