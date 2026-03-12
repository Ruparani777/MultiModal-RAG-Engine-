"""
test_ingestion.py — Unit tests for the ingestion pipeline.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.document_processor import _chunk_text, extract_from_text
from src.models import ChunkType, DocumentType


# ─── Text Chunking ────────────────────────────────────────────────────────────

class TestChunkText:
    def test_basic_chunking(self):
        text = "A" * 2000
        chunks = list(_chunk_text(text, chunk_size=800, overlap=150))
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 800

    def test_empty_text(self):
        chunks = list(_chunk_text("", 800, 150))
        assert chunks == []

    def test_short_text_single_chunk(self):
        text = "Hello world"
        chunks = list(_chunk_text(text, 800, 150))
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_overlap(self):
        text = "A" * 1000
        chunks = list(_chunk_text(text, chunk_size=500, overlap=100))
        assert len(chunks) == 3  # 0-500, 400-900, 800-1000

    def test_whitespace_stripped(self):
        text = "  hello  "
        chunks = list(_chunk_text(text, 800, 150))
        assert chunks[0] == "hello"


# ─── Text File Extraction ─────────────────────────────────────────────────────

class TestExtractFromText:
    def test_basic_text_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a test document. " * 100)
            tmp_path = Path(f.name)

        try:
            chunks, images = extract_from_text(tmp_path, doc_id="test123")
            assert len(chunks) > 0
            assert len(images) == 0
            assert all(c.chunk_type == ChunkType.TEXT for c in chunks)
            assert all(c.doc_type == DocumentType.TEXT for c in chunks)
        finally:
            tmp_path.unlink()

    def test_chunk_ids_are_unique(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Content " * 500)
            tmp_path = Path(f.name)

        try:
            chunks, _ = extract_from_text(tmp_path, doc_id="test123")
            ids = [c.chunk_id for c in chunks]
            assert len(ids) == len(set(ids))
        finally:
            tmp_path.unlink()


# ─── Image Captioning (mocked) ────────────────────────────────────────────────

class TestImageCaptioner:
    @patch("src.ingestion.image_captioner._caption_with_openai")
    def test_caption_image_openai(self, mock_caption):
        from src.ingestion.image_captioner import caption_image
        from src.models import ImageData

        mock_caption.return_value = "A bar chart showing monthly revenue trends."

        img = ImageData(image_index=0, base64_data="fake_base64", width=100, height=100)
        with patch("src.ingestion.image_captioner.settings") as mock_settings:
            mock_settings.llm_provider = "openai"
            mock_settings.openai_api_key = "test"
            caption = caption_image(img)

        assert caption == "A bar chart showing monthly revenue trends."

    @patch("src.ingestion.image_captioner._caption_with_openai")
    def test_caption_failure_returns_fallback(self, mock_caption):
        from src.ingestion.image_captioner import caption_image
        from src.models import ImageData

        mock_caption.side_effect = Exception("API error")

        img = ImageData(image_index=0, base64_data="fake", width=100, height=100)
        with patch("src.ingestion.image_captioner.settings") as mock_settings:
            mock_settings.llm_provider = "openai"
            caption = caption_image(img)

        assert "unavailable" in caption.lower()


# ─── Embedder (mocked) ────────────────────────────────────────────────────────

class TestEmbedder:
    @patch("src.ingestion.embedder._get_openai_client")
    def test_embed_texts(self, mock_client_fn):
        from src.ingestion.embedder import embed_texts

        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client

        mock_embed_data = [MagicMock(embedding=[0.1] * 1536) for _ in range(3)]
        mock_client.embeddings.create.return_value = MagicMock(data=mock_embed_data)

        embeddings = embed_texts(["text1", "text2", "text3"])
        assert len(embeddings) == 3
        assert len(embeddings[0]) == 1536

    def test_embed_empty_list(self):
        from src.ingestion.embedder import embed_texts
        result = embed_texts([])
        assert result == []
