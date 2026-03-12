"""
main.py — FastAPI application exposing the MultiModal RAG Engine as a REST API.

Endpoints:
  POST /ingest          — Upload and ingest a document
  POST /query           — Query the knowledge base
  GET  /query/stream    — Streaming query (SSE)
  GET  /documents       — List ingested documents
  DELETE /documents/{id} — Delete a document
  GET  /health          — Health check
"""
from __future__ import annotations

import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.config import get_settings
from src.generation.generator import generate, stream_generate
from src.ingestion.pipeline import ingest_document
from src.logger import get_logger
from src.models import HealthResponse, IngestedDocument, QueryRequest, RAGResponse
from src.retrieval.retriever import retrieve
from src.retrieval.vector_store import get_vector_store

logger = get_logger(__name__)
settings = get_settings()

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".md", ".docx"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 MultiModal RAG Engine starting…")
    # Pre-warm vector store
    get_vector_store()
    logger.info(f"✓ Ready — LLM: {settings.llm_provider}/{settings.llm_model}")
    yield
    logger.info("Shutting down…")


app = FastAPI(
    title="MultiModal RAG Engine",
    description="Ingest PDFs, images, and documents. Query across text and visual content.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check system status."""
    vs = get_vector_store()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        vector_store_docs=vs.count(),
        llm_provider=f"{settings.llm_provider}/{settings.llm_model}",
    )


# ─── Ingestion ────────────────────────────────────────────────────────────────

@app.post("/ingest", response_model=IngestedDocument, tags=["Ingestion"])
async def ingest_file(file: UploadFile = File(...)):
    """
    Upload and ingest a document into the knowledge base.

    Supported formats: PDF, PNG, JPG, WEBP, TXT, MD, DOCX
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    # Save upload to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        result = ingest_document(tmp_path)
        # Rename doc_name to original filename
        result.doc_name = file.filename
        return result
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


# ─── Query ────────────────────────────────────────────────────────────────────

@app.post("/query", response_model=RAGResponse, tags=["Query"])
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base and get a generated answer with citations.
    """
    vs = get_vector_store()
    if vs.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="Knowledge base is empty. Please ingest documents first.",
        )

    chunks = retrieve(
        query=request.query,
        top_k=request.top_k,
        include_images=request.include_images,
    )
    response = generate(query=request.query, chunks=chunks)
    return response


@app.get("/query/stream", tags=["Query"])
async def stream_query(q: str, top_k: int = 5, include_images: bool = True):
    """
    Streaming query endpoint using Server-Sent Events.
    Usage: GET /query/stream?q=your+question
    """
    vs = get_vector_store()
    if vs.count() == 0:
        raise HTTPException(status_code=400, detail="Knowledge base is empty.")

    chunks = retrieve(query=q, top_k=top_k, include_images=include_images)

    def event_stream():
        for token in stream_generate(q, chunks):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─── Documents ────────────────────────────────────────────────────────────────

@app.get("/documents", tags=["Documents"])
async def list_documents():
    """List all ingested documents."""
    vs = get_vector_store()
    docs = vs.list_documents()
    return {"documents": docs, "total": len(docs)}


@app.delete("/documents/{doc_id}", tags=["Documents"])
async def delete_document(doc_id: str):
    """Delete all chunks for a given document ID."""
    vs = get_vector_store()
    deleted = vs.delete_document(doc_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    return {"deleted_chunks": deleted, "doc_id": doc_id}


@app.delete("/reset", tags=["System"])
async def reset_knowledge_base():
    """⚠️  Delete ALL data from the knowledge base."""
    vs = get_vector_store()
    vs.reset()
    return {"status": "reset complete"}
