from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database.base import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    default_educational_level = Column(String)  # K12, UNDERGRADUATE, GRADUATE
    default_format = Column(String)  # PDF, DOCX, HTML
    default_style = Column(String)
    include_exercises_by_default = Column(Boolean, default=True)
    include_summaries_by_default = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="user_preferences")

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, default_format={self.default_format})>"