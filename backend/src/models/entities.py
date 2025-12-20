from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from typing import Optional

class BookContentType(str, Enum):
    TEXT = "text"
    CODE = "code"
    FIGURE = "figure"
    TABLE = "table"


class BookContent(BaseModel):
    """Book content entity with all required attributes for retrieval"""
    book_id: str
    chapter: str
    section: str
    paragraph_index: int
    page_number: Optional[int] = None
    content_type: BookContentType
    content: str
    chunk_id: str
    # embedding_vector would be stored separately in vector DB
    metadata: Optional[Dict[str, Any]] = {}


class RetrievedChunk(BaseModel):
    """Represents a chunk retrieved from vector database"""
    chunk_id: str
    book_id: str
    chapter: str
    section: str
    paragraph_index: int
    content: str
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = {}


class QueryMode(str, Enum):
    FULL_BOOK = "full_book"
    SELECTED_TEXT = "selected_text"


class UserQuery(BaseModel):
    """Represents a user query to the system"""
    query_id: Optional[str] = None
    user_id: Optional[str] = None  # For tracking, optional
    query_text: str
    query_timestamp: Optional[datetime] = None
    selected_text: Optional[str] = None  # For selected text mode
    mode: QueryMode = QueryMode.FULL_BOOK
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the chatbot"""
    response_id: str
    query_id: str
    answer: str
    citations: List[Dict[str, Any]]  # List of citation objects
    session_id: Optional[str] = None
    is_fallback_response: bool = False
    based_on: Optional[str] = None  # Specifies if response is based on "full_book" or "selected_text"


class QueryLog(BaseModel):
    """Log entry for user queries and responses"""
    log_id: Optional[str] = None
    query_id: str
    query_text: str
    response_id: str
    response_text: str
    processing_time: Optional[float] = None
    user_feedback: Optional[str] = None
    log_timestamp: Optional[datetime] = None


class BookMetadata(BaseModel):
    """Metadata about a specific book"""
    book_id: str
    title: str
    author: str
    chapters_count: int
    indexed: bool
    last_indexed: Optional[datetime] = None