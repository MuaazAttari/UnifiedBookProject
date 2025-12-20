from typing import List, Dict, Any, Optional
from src.models.entities import BookContent, BookMetadata
from src.services.embedding_service import embedding_service
from src.config.qdrant_config import qdrant_service
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
import asyncio
import logging
from datetime import datetime, timedelta


class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=30)  # 30 minute session timeout
        self.logger = logging.getLogger("rag_chatbot")
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new session and return the session ID"""
        import uuid
        session_id = session_id or str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "queries": []
        }
        
        self.logger.info(f"Created new session: {session_id}")
        return session_id
    
    def is_session_valid(self, session_id: str) -> bool:
        """Check if a session is still valid (not expired)"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        time_since_last_activity = datetime.utcnow() - session["last_activity"]
        
        if time_since_last_activity > self.session_timeout:
            self.logger.info(f"Session {session_id} has expired")
            del self.active_sessions[session_id]
            return False
        
        return True
    
    def record_query(self, session_id: str, query: str, response: str):
        """Record a query in the session"""
        if not self.is_session_valid(session_id):
            session_id = self.create_session(session_id)
        
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.utcnow()
            self.active_sessions[session_id]["queries"].append({
                "query": query,
                "response": response,
                "timestamp": datetime.utcnow()
            })
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = []
        current_time = datetime.utcnow()
        
        for session_id, session_data in self.active_sessions.items():
            time_since_last_activity = current_time - session_data["last_activity"]
            if time_since_last_activity > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            self.logger.info(f"Cleaned up expired session: {session_id}")


class BookService:
    def __init__(self):
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
        self.session_manager = SessionManager()
    
    async def index_book_content(self, book_contents: List[BookContent]):
        """Index book content by generating embeddings and storing in Qdrant"""
        # Generate embeddings for the book content
        embeddings_data = self.embedding_service.embed_book_content(book_contents)
        
        # Store in Qdrant vector database
        self.qdrant_service.upsert_vectors(embeddings_data)
    
    async def get_book_metadata(self, book_id: str) -> Optional[BookMetadata]:
        """Get metadata for a specific book"""
        # This would typically query the database for book information
        # For now, returning a stub implementation
        # In a real implementation, this would query a database
        return BookMetadata(
            book_id=book_id,
            title="Sample Book Title",
            author="Sample Author",
            chapters_count=10,  # Placeholder
            indexed=True,  # Placeholder
            last_indexed=datetime.utcnow()  # Placeholder
        )
    
    async def search_book_content(self, 
                                 book_id: str, 
                                 query_text: str, 
                                 top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant content in the book using vector similarity"""
        # Generate embedding for the query
        # query_embedding = self.embedding_service.generate_embeddings([query_text])[0]
        # query_embedding = self.embedding_service.embed_query(query_text)
        # query_embedding = self.embedding_service.generate_embeddings([query_text])[0]
        query_embedding = self.embedding_service.embed_text(query_text)



        # Search in Qdrant
        search_results = self.qdrant_service.search_vectors(
            query_vector=query_embedding,
            top_k=top_k
        )
        
        # Format results
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "chunk_id": result.payload["chunk_id"],
                "book_id": result.payload["book_id"],
                "chapter": result.payload["chapter"],
                "section": result.payload["section"],
                "paragraph_index": result.payload["paragraph_index"],
                "content": result.payload["content"],
                "relevance_score": result.score
            })
        
        return formatted_results


# Global instance
book_service = BookService()