"""
Database service for logging and persistence
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from src.models.entities import QueryLog
from src.models.database import get_db_session
from src.config.settings import settings
from datetime import datetime


class DatabaseService:
    def __init__(self):
        # Use the database session from our existing database module
        pass
    
    async def log_query(self, 
                       query_id: str, 
                       query_text: str, 
                       response_id: str, 
                       response_text: str, 
                       processing_time: Optional[float] = None,
                       user_feedback: Optional[str] = None):
        """Log a user query and response to the database"""
        # Create a QueryLog instance
        query_log = QueryLog(
            query_id=query_id,
            query_text=query_text,
            response_id=response_id,
            response_text=response_text,
            processing_time=processing_time,
            user_feedback=user_feedback,
            log_timestamp=datetime.utcnow()
        )
        
        # In a real implementation, we would connect to the database and insert the log
        # For now, we'll just simulate the logging behavior
        print(f"LOGGED QUERY: {query_id[:8]}... - {query_text[:30]}...")
        

# Global instance
database_service = DatabaseService()