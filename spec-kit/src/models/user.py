from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.sql import func
import uuid

from src.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    software_experience = Column(String, nullable=True)  # beginner, intermediate, expert
    hardware_availability = Column(String, nullable=True)
    robotics_familiarity = Column(String, nullable=True)  # beginner, intermediate, expert
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)


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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())