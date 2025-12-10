from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
import uuid

from src.db.database import Base


class PersonalizationProfile(Base):
    __tablename__ = "personalization_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users.id
    chapter_id = Column(String, nullable=False, index=True)  # Foreign key to chapters.id
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, expert
    content_preferences = Column(Text, nullable=True)  # JSON string of content preferences
    learning_style = Column(String, nullable=True)  # visual, hands_on, theoretical
    personalization_enabled = Column(Boolean, default=False)
    custom_preferences = Column(Text, nullable=True)  # Additional custom preferences as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())