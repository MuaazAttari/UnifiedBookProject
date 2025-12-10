from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func

from src.db.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context_type = Column(String, nullable=False)  # "full_book" or "selected_text"
    selected_text = Column(Text, nullable=True)
    query_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    response_timestamp = Column(DateTime(timezone=True), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)