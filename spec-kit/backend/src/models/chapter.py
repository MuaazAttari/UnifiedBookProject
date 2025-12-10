from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .user import Base

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(Text)
    position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String)  # DRAFT, GENERATING, COMPLETED, REVIEWED
    textbook_id = Column(String, ForeignKey("textbooks.id"))

    # Relationships
    textbook = relationship("Textbook", back_populates="chapters_relationship")
    sections_relationship = relationship("Section", back_populates="chapter", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chapter(id={self.id}, title={self.title}, position={self.position})>"