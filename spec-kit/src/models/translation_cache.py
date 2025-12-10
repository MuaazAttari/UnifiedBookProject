from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
import uuid

from src.db.database import Base


class TranslationCache(Base):
    __tablename__ = "translation_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_text_hash = Column(String, nullable=False, index=True)  # Hash of the source text for quick lookup
    source_text = Column(Text, nullable=False)  # Original text
    target_language = Column(String, nullable=False)  # e.g., 'ur', 'es', 'fr'
    translated_text = Column(Text, nullable=False)  # Translated text
    source_language = Column(String, default="en")  # Source language (default English)
    is_cached = Column(Boolean, default=True)  # Whether this is a cached translation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())