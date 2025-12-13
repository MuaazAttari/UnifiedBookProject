"""
Configuration for RAG chat functionality
"""
from pydantic_settings import BaseSettings
from typing import Optional


class RAGSettings(BaseSettings):
    # Cohere settings
    cohere_api_key: Optional[str] = None
    cohere_model: str = "embed-english-v3.0"

    # Qdrant settings
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "physical_ai_docs"

    # Retrieval settings
    rag_default_topk: int = 5
    chunk_size: int = 512
    max_tokens: int = 2048

    # CCR Qwen settings
    ccr_qwen_token: Optional[str] = None
    ccr_qwen_url: str = "https://api.claude-router.com/v1/chat/completions"  # Placeholder URL

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = 'ignore'  # Ignore extra fields from the env file


# Global instance
rag_settings = RAGSettings()