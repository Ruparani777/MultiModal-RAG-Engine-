"""
image_captioner.py — Generates rich semantic captions for images using a Vision LLM.

Uses GPT-4o (default) or Claude claude-sonnet-4-20250514 depending on settings.
Captions are stored as text chunks in the vector store, enabling image search.
"""
from __future__ import annotations

import time
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings
from src.logger import get_logger
from src.models import ChunkType, DocumentChunk, DocumentType, ImageData

logger = get_logger(__name__)
settings = get_settings()

CAPTION_PROMPT = """You are analyzing an image extracted from a document.
Provide a detailed, informative description that captures:
1. The main subject and content of the image
2. Any text, labels, titles, or annotations visible
3. Charts/graphs: describe axes, trends, key data points
4. Diagrams/figures: explain the structure and relationships shown
5. Tables: summarize the data and key insights
6. Photos: describe scene, objects, people (no names), context

Be specific and detailed. This description will be used for semantic search, 
so include relevant keywords and concepts a user might search for.

Respond with ONLY the description, no preamble."""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _caption_with_openai(base64_data: str) -> str:
    import openai
    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.vision_model,
        max_tokens=400,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_data}", "detail": "high"},
                    },
                    {"type": "text", "text": CAPTION_PROMPT},
                ],
            }
        ],
    )
    return response.choices[0].message.content.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _caption_with_anthropic(base64_data: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.vision_model,
        max_tokens=400,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_data,
                        },
                    },
                    {"type": "text", "text": CAPTION_PROMPT},
                ],
            }
        ],
    )
    return response.content[0].text.strip()


def caption_image(image_data: ImageData) -> str:
    """Generate a caption for a single image using the configured vision model."""
    try:
        if settings.llm_provider == "anthropic":
            caption = _caption_with_anthropic(image_data.base64_data)
        else:
            caption = _caption_with_openai(image_data.base64_data)
        logger.info(f"  ↳ Captioned image {image_data.image_index} ({len(caption)} chars)")
        return caption
    except Exception as e:
        logger.error(f"Caption failed for image {image_data.image_index}: {e}")
        return f"[Image {image_data.image_index} — caption unavailable]"


def caption_images_to_chunks(
    images: list[ImageData],
    doc_id: str,
    doc_name: str,
    doc_type: DocumentType,
) -> list[DocumentChunk]:
    """
    Convert a list of ImageData objects into DocumentChunk objects 
    by generating captions via the vision LLM.
    """
    import uuid

    if not images:
        return []

    logger.info(f"Captioning {len(images)} image(s) from '{doc_name}'…")
    chunks = []

    for img in images:
        caption = caption_image(img)
        img.caption = caption  # store caption back on the object

        content = (
            f"[Image on page {img.page_number}] {caption}"
            if img.page_number
            else f"[Image] {caption}"
        )

        chunks.append(
            DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                doc_name=doc_name,
                doc_type=doc_type,
                chunk_type=ChunkType.IMAGE_CAPTION,
                content=content,
                page_number=img.page_number,
                image_index=img.image_index,
                metadata={
                    "image_width": img.width,
                    "image_height": img.height,
                    "image_format": img.format,
                },
            )
        )

    return chunks
