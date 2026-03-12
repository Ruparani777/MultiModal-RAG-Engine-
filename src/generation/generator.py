"""
generator.py — Final generation step: assembles context and calls the LLM.

Supports:
- OpenAI (GPT-4o)
- Anthropic (Claude)
- Streaming mode
"""
from __future__ import annotations

import time
from collections.abc import Generator

from src.config import get_settings
from src.logger import get_logger
from src.models import Citation, ChunkType, RAGResponse, RetrievedChunk

logger = get_logger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are an intelligent assistant with access to a curated knowledge base.
Answer questions based ONLY on the provided context. Be accurate, detailed, and helpful.

Rules:
- Base your answer strictly on the provided context
- If the context doesn't contain the answer, say so clearly
- Cite specific sources when mentioning facts
- For image-based context, reference what was described in the image
- Be concise but complete"""


def _build_context(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a context string for the LLM."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.doc_name
        if chunk.page_number:
            source += f" (page {chunk.page_number})"
        if chunk.chunk_type == ChunkType.IMAGE_CAPTION:
            source += " [IMAGE]"

        parts.append(f"[Source {i}: {source}]\n{chunk.content}")

    return "\n\n---\n\n".join(parts)


def _build_user_message(query: str, context: str) -> str:
    return f"""Context:
{context}

---
Question: {query}

Please answer based on the context above."""


def _generate_openai(query: str, context: str) -> str:
    import openai
    client = openai.OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=1500,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(query, context)},
        ],
    )
    return response.choices[0].message.content.strip()


def _generate_anthropic(query: str, context: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": _build_user_message(query, context)},
        ],
    )
    return response.content[0].text.strip()


def _stream_openai(query: str, context: str) -> Generator[str, None, None]:
    import openai
    client = openai.OpenAI(api_key=settings.openai_api_key)
    stream = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=1500,
        temperature=0.1,
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(query, context)},
        ],
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def _stream_anthropic(query: str, context: str) -> Generator[str, None, None]:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    with client.messages.stream(
        model=settings.llm_model,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_message(query, context)}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def _build_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            doc_name=c.doc_name,
            chunk_type=c.chunk_type,
            page_number=c.page_number,
            relevance_score=c.score,
        )
        for c in chunks
    ]


# ─── Public API ───────────────────────────────────────────────────────────────

def generate(query: str, chunks: list[RetrievedChunk]) -> RAGResponse:
    """
    Generate a RAG answer from retrieved chunks.

    Args:
        query: User's question
        chunks: Retrieved context chunks

    Returns:
        RAGResponse with answer, citations, and metadata
    """
    start = time.time()

    if not chunks:
        return RAGResponse(
            query=query,
            answer="I couldn't find relevant information in the knowledge base to answer your question.",
            citations=[],
            retrieved_chunks=[],
            model_used=settings.llm_model,
            processing_time_sec=0.0,
        )

    context = _build_context(chunks)
    logger.info(f"Generating answer (provider={settings.llm_provider}, model={settings.llm_model})")

    if settings.llm_provider == "anthropic":
        answer = _generate_anthropic(query, context)
    else:
        answer = _generate_openai(query, context)

    elapsed = time.time() - start
    logger.info(f"  ✓ Generated answer in {elapsed:.2f}s")

    return RAGResponse(
        query=query,
        answer=answer,
        citations=_build_citations(chunks),
        retrieved_chunks=chunks,
        model_used=settings.llm_model,
        processing_time_sec=round(elapsed, 2),
    )


def stream_generate(
    query: str,
    chunks: list[RetrievedChunk],
) -> Generator[str, None, None]:
    """
    Streaming version of generate(). Yields answer tokens as they arrive.
    """
    if not chunks:
        yield "I couldn't find relevant information in the knowledge base."
        return

    context = _build_context(chunks)

    if settings.llm_provider == "anthropic":
        yield from _stream_anthropic(query, context)
    else:
        yield from _stream_openai(query, context)
