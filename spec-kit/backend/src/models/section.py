from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .user import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    content = Column(Text)
    position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    type = Column(String)  # CONTENT, SUMMARY, EXERCISE, KEY_POINT
    chapter_id = Column(String, ForeignKey("chapters.id"))

    # Relationships
    chapter = relationship("Chapter", back_populates="sections_relationship")

    def __repr__(self):
        return f"<Section(id={self.id}, title={self.title}, type={self.type})>"