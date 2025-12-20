from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    # API Keys and service URLs
    # cohere_api_key: str = Field(..., alias="COHERE_API_KEY")
    qdrant_api_key: str = Field(..., alias="QDRANT_API_KEY")
    qdrant_cluster_url: str = Field(..., alias="QDRANT_CLUSTER_URL")
    neon_database_url: str = Field(..., alias="NEON_DATABASE_URL")
    
    # Application settings
    app_name: str = "RAG Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    # Qdrant settings
    qdrant_collection_name: str = "book_content"
    hf_api_token: str
    # GROQ_API_KEY: str
    # Cohere settings
    # cohere_model: str = "command-r-plus"
    # cohere_embedding_model: str = "embed-multilingual-v3.0"
    
    # Retrieval settings
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.5
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        # case_sensitive = True


settings = Settings()