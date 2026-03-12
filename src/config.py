"""
config.py — Centralized configuration with Pydantic Settings.
Reads from .env file automatically.
"""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    vision_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Vector Store
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "multimodal_rag"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 150
    max_image_size_mb: int = 20

    # Retrieval
    top_k_results: int = 5
    similarity_threshold: float = 0.3

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Logging
    log_level: str = "INFO"

    @property
    def chroma_persist_path(self) -> Path:
        path = Path(self.chroma_persist_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
