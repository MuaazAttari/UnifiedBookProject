from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from src.db.database import Base
import uuid


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserBackgroundQuestionnaire(Base):
    """Model for storing user background questionnaire responses."""

    __tablename__ = "user_background_questionnaire"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users table
    education_level = Column(String, nullable=True)  # e.g., "high_school", "undergraduate", "graduate", "professional"
    technical_background = Column(Text, nullable=True)  # Free text about technical experience
    learning_goals = Column(Text, nullable=True)  # What the user wants to learn
    preferred_learning_style = Column(String, nullable=True)  # e.g., "visual", "hands_on", "theoretical"
    experience_with_ai = Column(String, nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    experience_with_robotics = Column(String, nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    timezone = Column(String, nullable=True)  # User's timezone
    additional_notes = Column(Text, nullable=True)  # Any additional information
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())