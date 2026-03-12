# 🔍 MultiModal RAG Engine

A production-grade Retrieval-Augmented Generation (RAG) system that ingests **PDFs, images, and text documents** and answers natural language questions using both text and visual context.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.112+-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION PIPELINE                          │
│                                                                 │
│  PDF/Image/Text ──► DocumentProcessor ──► Text Chunks          │
│                              │                                  │
│                              └──► Images ──► VisionLLM         │
│                                              (GPT-4o / Claude) │
│                                                   │             │
│                                            Image Captions       │
│                                                   │             │
│                    All Chunks ◄───────────────────┘            │
│                         │                                       │
│                    Embedder (text-embedding-3-small)            │
│                         │                                       │
│                    ChromaDB (persistent)                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      QUERY PIPELINE                             │
│                                                                 │
│  User Query ──► Embed Query ──► ChromaDB Similarity Search     │
│                                           │                     │
│                              Top-K Chunks (text + images)      │
│                                           │                     │
│                              Context Assembly                   │
│                                           │                     │
│                              LLM (GPT-4o / Claude)             │
│                                           │                     │
│                         Answer + Citations + Metadata           │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Features

| Feature | Details |
|--------|---------|
| 📄 **Multi-format ingestion** | PDF, PNG, JPG, WEBP, TXT, MD, DOCX |
| 🖼️ **Multimodal understanding** | Images captioned by GPT-4o / Claude Vision |
| 🔍 **Semantic search** | OpenAI `text-embedding-3-small` embeddings |
| 💾 **Persistent vector store** | ChromaDB with cosine similarity |
| ⚡ **Streaming responses** | Token-by-token generation |
| 📎 **Source citations** | Page numbers + similarity scores |
| 🔌 **REST API** | FastAPI with OpenAPI docs |
| 🎨 **Chat UI** | Streamlit with file uploader |
| 🐳 **Docker support** | docker-compose for full stack |
| 🧪 **Test suite** | pytest with mocking |

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/multimodal-rag.git
cd multimodal-rag
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### 3. Ingest Documents

```bash
# Single file
python scripts/ingest.py data/samples/report.pdf

# Entire folder
python scripts/ingest.py data/samples/
```

### 4A. Launch the Chat UI (Streamlit)

```bash
streamlit run ui/app.py
# Visit http://localhost:8501
```

### 4B. Launch the REST API

```bash
uvicorn src.api.main:app --reload
# Visit http://localhost:8000/docs
```

### 4C. Query from CLI

```bash
python scripts/query.py "What are the key findings in the report?"
python scripts/query.py "Describe the charts on page 3" --top-k 8
```

## 🐳 Docker

```bash
# Copy and fill in your API keys
cp .env.example .env

# Start both API + UI
docker-compose up --build

# API:  http://localhost:8000
# UI:   http://localhost:8501
# Docs: http://localhost:8000/docs
```

## 🔌 API Reference

### Ingest a Document

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@report.pdf"
```

### Query the Knowledge Base

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main conclusions?", "top_k": 5}'
```

### Streaming Query

```bash
curl "http://localhost:8000/query/stream?q=summarize+the+document"
```

### List Documents

```bash
curl http://localhost:8000/documents
```

## 📁 Project Structure

```
multimodal-rag/
├── src/
│   ├── config.py              # Pydantic settings
│   ├── models.py              # Shared data models
│   ├── logger.py              # Rich logging
│   ├── ingestion/
│   │   ├── document_processor.py  # PDF/image/text extraction
│   │   ├── image_captioner.py     # Vision LLM captioning
│   │   ├── embedder.py            # OpenAI embeddings
│   │   └── pipeline.py            # End-to-end ingestion
│   ├── retrieval/
│   │   ├── vector_store.py        # ChromaDB wrapper
│   │   └── retriever.py           # Query + retrieve
│   ├── generation/
│   │   └── generator.py           # LLM answer generation
│   └── api/
│       └── main.py                # FastAPI application
├── ui/
│   └── app.py                 # Streamlit chat interface
├── tests/
│   ├── test_ingestion.py
│   └── test_retrieval_generation.py
├── scripts/
│   ├── ingest.py              # CLI ingestion
│   └── query.py               # CLI querying
├── data/
│   └── samples/               # Place test documents here
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── .env.example
```

## ⚙️ Configuration

All settings are in `.env`:

| Variable | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key (optional) |
| `LLM_PROVIDER` | `openai` | `openai` or `anthropic` |
| `LLM_MODEL` | `gpt-4o` | Generation model |
| `VISION_MODEL` | `gpt-4o` | Vision model for image captioning |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `800` | Max chars per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Default retrieval count |

## 🧪 Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

## 🔮 Potential Extensions

- **Re-ranking**: Add a cross-encoder reranker (e.g., `ms-marco-MiniLM`) after retrieval
- **Hybrid search**: Combine dense vectors with BM25 sparse retrieval
- **Multi-hop reasoning**: Chain multiple retrieval steps for complex queries
- **Evaluation**: Add RAGAs metrics (faithfulness, answer relevancy, context recall)
- **Auth**: Add API key authentication to FastAPI endpoints
- **Cloud deployment**: Deploy to AWS/GCP with managed vector store (Pinecone/Weaviate)

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
