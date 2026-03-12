"""
document_processor.py — Extracts text and images from PDFs, images, and text files.

Supports:
- PDF  → text per page + embedded images
- Images (PNG/JPG/WEBP) → raw image for captioning
- TXT / MD  → plain text
- DOCX → text extraction
"""
from __future__ import annotations

import base64
import hashlib
import io
import time
import uuid
from pathlib import Path
from typing import Generator

import fitz  # PyMuPDF
from PIL import Image

from src.config import get_settings
from src.logger import get_logger
from src.models import ChunkType, DocumentChunk, DocumentType, ImageData, IngestedDocument

logger = get_logger(__name__)
settings = get_settings()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _detect_doc_type(file_path: Path) -> DocumentType:
    suffix = file_path.suffix.lower()
    return {
        ".pdf": DocumentType.PDF,
        ".png": DocumentType.IMAGE,
        ".jpg": DocumentType.IMAGE,
        ".jpeg": DocumentType.IMAGE,
        ".webp": DocumentType.IMAGE,
        ".gif": DocumentType.IMAGE,
        ".bmp": DocumentType.IMAGE,
        ".txt": DocumentType.TEXT,
        ".md": DocumentType.TEXT,
        ".docx": DocumentType.DOCX,
    }.get(suffix, DocumentType.UNKNOWN)


def _make_doc_id(file_path: Path) -> str:
    """Deterministic doc ID based on filename + mtime."""
    content = f"{file_path.name}-{file_path.stat().st_mtime}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


def _image_to_base64(img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _chunk_text(text: str, chunk_size: int, overlap: int) -> Generator[str, None, None]:
    """Simple sliding-window text chunker."""
    text = text.strip()
    if not text:
        return
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= len(text):
            break
        start += chunk_size - overlap


# ─── Extractors ───────────────────────────────────────────────────────────────

def extract_from_pdf(
    file_path: Path,
    doc_id: str,
) -> tuple[list[DocumentChunk], list[ImageData]]:
    """Extract text chunks and images from a PDF file."""
    text_chunks: list[DocumentChunk] = []
    images: list[ImageData] = []
    image_counter = 0

    doc = fitz.open(str(file_path))
    logger.info(f"[PDF] {file_path.name} — {len(doc)} pages")

    for page_num, page in enumerate(doc, start=1):
        # ── Text ──────────────────────────────────────────────
        page_text = page.get_text("text").strip()
        if page_text:
            for chunk_text in _chunk_text(page_text, settings.chunk_size, settings.chunk_overlap):
                text_chunks.append(
                    DocumentChunk(
                        chunk_id=str(uuid.uuid4()),
                        doc_id=doc_id,
                        doc_name=file_path.name,
                        doc_type=DocumentType.PDF,
                        chunk_type=ChunkType.TEXT,
                        content=chunk_text,
                        page_number=page_num,
                        metadata={"source": str(file_path), "page": page_num},
                    )
                )

        # ── Images ────────────────────────────────────────────
        image_list = page.get_images(full=True)
        for img_info in image_list:
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                img_fmt = base_image["ext"].upper()
                if img_fmt == "JPX":
                    img_fmt = "JPEG"

                pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                w, h = pil_img.size

                # Skip tiny icons
                if w < 50 or h < 50:
                    continue

                # Resize large images to save tokens
                max_px = 1024
                if max(w, h) > max_px:
                    ratio = max_px / max(w, h)
                    pil_img = pil_img.resize((int(w * ratio), int(h * ratio)))

                images.append(
                    ImageData(
                        image_index=image_counter,
                        page_number=page_num,
                        base64_data=_image_to_base64(pil_img),
                        width=pil_img.width,
                        height=pil_img.height,
                        format="PNG",
                    )
                )
                image_counter += 1
            except Exception as e:
                logger.warning(f"Could not extract image xref={xref}: {e}")

    doc.close()
    return text_chunks, images


def extract_from_image(
    file_path: Path,
    doc_id: str,
) -> tuple[list[DocumentChunk], list[ImageData]]:
    """Load an image file — no text chunks, just raw image data."""
    pil_img = Image.open(file_path).convert("RGB")
    w, h = pil_img.size

    # Resize if too large
    max_px = 1024
    if max(w, h) > max_px:
        ratio = max_px / max(w, h)
        pil_img = pil_img.resize((int(w * ratio), int(h * ratio)))

    image_data = ImageData(
        image_index=0,
        page_number=None,
        base64_data=_image_to_base64(pil_img),
        width=pil_img.width,
        height=pil_img.height,
        format="PNG",
    )
    logger.info(f"[IMAGE] {file_path.name} — {pil_img.width}x{pil_img.height}")
    return [], [image_data]


def extract_from_text(
    file_path: Path,
    doc_id: str,
) -> tuple[list[DocumentChunk], list[ImageData]]:
    """Extract chunks from plain text / markdown files."""
    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    chunks = []
    for chunk_text in _chunk_text(raw, settings.chunk_size, settings.chunk_overlap):
        chunks.append(
            DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                doc_name=file_path.name,
                doc_type=DocumentType.TEXT,
                chunk_type=ChunkType.TEXT,
                content=chunk_text,
                metadata={"source": str(file_path)},
            )
        )
    logger.info(f"[TEXT] {file_path.name} — {len(chunks)} chunks")
    return chunks, []


def extract_from_docx(
    file_path: Path,
    doc_id: str,
) -> tuple[list[DocumentChunk], list[ImageData]]:
    """Extract text from a .docx file."""
    try:
        from docx import Document as DocxDocument
    except ImportError:
        logger.warning("python-docx not installed, skipping DOCX extraction")
        return [], []

    docx = DocxDocument(str(file_path))
    full_text = "\n".join(p.text for p in docx.paragraphs if p.text.strip())
    chunks = []
    for chunk_text in _chunk_text(full_text, settings.chunk_size, settings.chunk_overlap):
        chunks.append(
            DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                doc_name=file_path.name,
                doc_type=DocumentType.DOCX,
                chunk_type=ChunkType.TEXT,
                content=chunk_text,
                metadata={"source": str(file_path)},
            )
        )
    logger.info(f"[DOCX] {file_path.name} — {len(chunks)} chunks")
    return chunks, []


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def process_document(file_path: Path) -> tuple[list[DocumentChunk], list[ImageData], str, DocumentType]:
    """
    Dispatch document to the correct extractor.

    Returns:
        (text_chunks, image_data_list, doc_id, doc_type)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    doc_type = _detect_doc_type(file_path)
    doc_id = _make_doc_id(file_path)

    if doc_type == DocumentType.PDF:
        chunks, images = extract_from_pdf(file_path, doc_id)
    elif doc_type == DocumentType.IMAGE:
        chunks, images = extract_from_image(file_path, doc_id)
    elif doc_type == DocumentType.TEXT:
        chunks, images = extract_from_text(file_path, doc_id)
    elif doc_type == DocumentType.DOCX:
        chunks, images = extract_from_docx(file_path, doc_id)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    return chunks, images, doc_id, doc_type
