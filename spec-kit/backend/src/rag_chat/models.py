"""
Models for RAG chat functionality
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..models.user import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous sessions
    title = Column(String, nullable=True)  # Auto-generated title from first message or summary
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous sessions
    role = Column(String)  # "user", "assistant", "system"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Store metadata about the retrieval context
    retrieved_context = Column(JSON, nullable=True)  # Stores doc_ids, scores, etc.

    # Relationships
    session = relationship("ChatSession", back_populates="messages")