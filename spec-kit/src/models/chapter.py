from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func

from src.db.database import Base


class Chapter(Base):
    __tablename__ = "chapters"

    chapter_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    frontmatter = Column(String, nullable=False)  # Stored as JSON string
    order = Column(Integer, nullable=False, unique=True)
    path = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())