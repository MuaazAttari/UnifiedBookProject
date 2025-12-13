from pydantic_settings import SettingsConfigDict, BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "Textbook Generation API"
    environment: str = "local"  # local, staging, or production
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: Optional[str] = None
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Database connection pooling settings
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_pre_ping: bool = True
    db_pool_recycle: int = 3600

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    log_file_max_size: int = 10 * 1024 * 1024  # 10MB
    log_file_backup_count: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_local(self) -> bool:
        return self.environment.lower() == "local"

    @property
    def is_staging(self) -> bool:
        return self.environment.lower() == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "railway"]

    @property
    def is_railway(self) -> bool:
        return self.environment.lower() == "railway"


settings = Settings()