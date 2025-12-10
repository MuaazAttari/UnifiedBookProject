import os
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Unified Textbook Generation and RAG System"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000", "http://localhost:8000"]

    # Database settings
    DATABASE_URL: PostgresDsn = Field(default=..., env="DATABASE_URL")

    # Qdrant settings
    QDRANT_URL: Optional[str] = Field(default=None, env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")

    # OpenAI settings
    OPENAI_API_KEY: str = Field(default=..., env="OPENAI_API_KEY")

    # Security settings
    SECRET_KEY: str = Field(default=..., env="JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Optional[List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()