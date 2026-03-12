"""
app.py — Streamlit UI for the MultiModal RAG Engine.

Features:
- Upload and ingest documents (PDF, images, text)
- Interactive chat interface with streaming
- Source citations with chunk type badges
- Document management sidebar
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make src importable
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.config import get_settings
from src.generation.generator import stream_generate
from src.ingestion.pipeline import ingest_document
from src.models import ChunkType
from src.retrieval.retriever import retrieve
from src.retrieval.vector_store import get_vector_store

settings = get_settings()

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="MultiModal RAG Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
.citation-box {
    background: #f0f4ff;
    border-left: 3px solid #4c72b0;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 4px 0;
    font-size: 0.85em;
}
.badge-text {
    background: #4c72b0;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.75em;
}
.badge-image {
    background: #2ea44f;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.75em;
}
.score-bar {
    font-size: 0.75em;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ingested_docs" not in st.session_state:
    st.session_state.ingested_docs = []


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("📚 Document Manager")
    st.caption(f"Provider: `{settings.llm_provider}` | Model: `{settings.llm_model}`")
    st.divider()

    # ── Upload ────────────────────────────────────────────────────────────────
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Drag & drop files here",
        type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "md", "docx"],
        accept_multiple_files=True,
        help="Supports PDF, images (PNG/JPG), and text files",
    )

    if uploaded_files:
        if st.button("⚡ Ingest All", type="primary", use_container_width=True):
            import tempfile

            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}…"):
                    try:
                        suffix = Path(uploaded_file.name).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(uploaded_file.read())
                            tmp_path = Path(tmp.name)

                        result = ingest_document(tmp_path)
                        result.doc_name = uploaded_file.name
                        tmp_path.unlink(missing_ok=True)

                        st.session_state.ingested_docs.append(result)
                        st.success(
                            f"✅ **{uploaded_file.name}**  \n"
                            f"{result.text_chunks} text chunks + {result.image_chunks} image chunks  \n"
                            f"⏱️ {result.processing_time_sec:.1f}s"
                        )
                    except Exception as e:
                        st.error(f"❌ {uploaded_file.name}: {e}")

    st.divider()

    # ── Knowledge Base Stats ──────────────────────────────────────────────────
    st.subheader("Knowledge Base")
    try:
        vs = get_vector_store()
        total = vs.count()
        docs = vs.list_documents()
        col1, col2 = st.columns(2)
        col1.metric("Chunks", total)
        col2.metric("Documents", len(docs))

        if docs:
            with st.expander("📄 Ingested Files", expanded=False):
                for doc in docs:
                    icon = "🖼️" if doc["doc_type"] == "image" else "📄"
                    st.caption(f"{icon} {doc['doc_name']}")

        if st.button("🗑️ Reset KB", type="secondary", use_container_width=True):
            vs.reset()
            st.session_state.messages = []
            st.session_state.ingested_docs = []
            st.rerun()
    except Exception as e:
        st.error(f"Vector store error: {e}")

    st.divider()

    # ── Settings ──────────────────────────────────────────────────────────────
    st.subheader("Query Settings")
    top_k = st.slider("Top-K Results", 1, 10, 5)
    include_images = st.checkbox("Include Image Context", value=True)


# ─── Main Chat ────────────────────────────────────────────────────────────────

st.title("🔍 MultiModal RAG Engine")
st.caption("Ask questions across your ingested PDFs, images, and documents")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander(f"📎 {len(msg['citations'])} source(s)", expanded=False):
                for i, cit in enumerate(msg["citations"], 1):
                    badge = (
                        '<span class="badge-image">IMAGE</span>'
                        if cit["chunk_type"] == "image_caption"
                        else '<span class="badge-text">TEXT</span>'
                    )
                    page_info = f"p.{cit['page_number']}" if cit.get("page_number") else ""
                    score = cit["score"]
                    st.markdown(
                        f'<div class="citation-box">'
                        f"{i}. {badge} <b>{cit['doc_name']}</b> {page_info} "
                        f'<span class="score-bar">score: {score:.3f}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

# Chat input
if prompt := st.chat_input("Ask a question about your documents…"):
    # Check KB is populated
    try:
        vs = get_vector_store()
        if vs.count() == 0:
            st.warning("⚠️ Knowledge base is empty. Please upload and ingest documents first.")
            st.stop()
    except Exception:
        st.error("Vector store unavailable.")
        st.stop()

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Retrieve + generate
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base…"):
            chunks = retrieve(query=prompt, top_k=top_k, include_images=include_images)

        if not chunks:
            answer = "I couldn't find relevant information in the knowledge base for your question."
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            # Streaming response
            answer_placeholder = st.empty()
            full_answer = ""

            for token in stream_generate(prompt, chunks):
                full_answer += token
                answer_placeholder.markdown(full_answer + "▌")
            answer_placeholder.markdown(full_answer)

            # Citations
            citations = [
                {
                    "doc_name": c.doc_name,
                    "chunk_type": c.chunk_type.value,
                    "page_number": c.page_number,
                    "score": c.score,
                }
                for c in chunks
            ]

            with st.expander(f"📎 {len(citations)} source(s)", expanded=False):
                for i, cit in enumerate(citations, 1):
                    badge = (
                        '<span class="badge-image">IMAGE</span>'
                        if cit["chunk_type"] == "image_caption"
                        else '<span class="badge-text">TEXT</span>'
                    )
                    page_info = f"p.{cit['page_number']}" if cit.get("page_number") else ""
                    score = cit["score"]
                    st.markdown(
                        f'<div class="citation-box">'
                        f"{i}. {badge} <b>{cit['doc_name']}</b> {page_info} "
                        f'<span class="score-bar">score: {score:.3f}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_answer,
                "citations": citations,
            })
