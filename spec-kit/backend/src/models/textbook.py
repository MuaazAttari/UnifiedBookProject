from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .user import Base

class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    subject = Column(String, index=True)
    educational_level = Column(String)  # K12, UNDERGRADUATE, GRADUATE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String)  # DRAFT, GENERATING, COMPLETED, REVIEWED
    user_id = Column(String, ForeignKey("users.id"))
    settings = Column(Text)  # JSON string for settings

    # Relationships
    user = relationship("User", back_populates="user_textbooks")
    chapters_relationship = relationship("Chapter", back_populates="textbook", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Textbook(id={self.id}, title={self.title}, subject={self.subject})>"