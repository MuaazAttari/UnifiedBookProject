import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.chat_session import ChatSession


class ChatSessionService:
    """Service class for managing chat sessions."""

    @staticmethod
    def get_chat_session(db: Session, session_id: str) -> Optional[ChatSession]:
        """
        Retrieve a chat session by ID.
        """
        return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    @staticmethod
    def get_chat_sessions(
        db: Session,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatSession]:
        """
        Retrieve chat sessions with optional filtering.
        """
        query = db.query(ChatSession)

        if user_id:
            query = query.filter(ChatSession.user_id == user_id)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_chat_session(
        db: Session,
        user_id: Optional[str],
        query: str,
        response: str,
        context_type: str,
        selected_text: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> ChatSession:
        """
        Create a new chat session.
        """
        session_id = str(uuid.uuid4())

        db_chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            query=query,
            response=response,
            context_type=context_type,
            selected_text=selected_text,
            tokens_used=tokens_used
        )

        db.add(db_chat_session)
        db.commit()
        db.refresh(db_chat_session)

        return db_chat_session

    @staticmethod
    def update_chat_session(
        db: Session,
        session_id: str,
        query: Optional[str] = None,
        response: Optional[str] = None,
        context_type: Optional[str] = None,
        selected_text: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> Optional[ChatSession]:
        """
        Update an existing chat session.
        """
        db_chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if db_chat_session:
            if query is not None:
                db_chat_session.query = query
            if response is not None:
                db_chat_session.response = response
            if context_type is not None:
                db_chat_session.context_type = context_type
            if selected_text is not None:
                db_chat_session.selected_text = selected_text
            if tokens_used is not None:
                db_chat_session.tokens_used = tokens_used

            db.commit()
            db.refresh(db_chat_session)

        return db_chat_session

    @staticmethod
    def delete_chat_session(db: Session, session_id: str) -> bool:
        """
        Delete a chat session.
        """
        db_chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if db_chat_session:
            db.delete(db_chat_session)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_chat_sessions(db: Session, user_id: str) -> List[ChatSession]:
        """
        Get all chat sessions for a specific user.
        """
        return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

    @staticmethod
    def get_recent_sessions(db: Session, limit: int = 10) -> List[ChatSession]:
        """
        Get the most recent chat sessions.
        """
        return db.query(ChatSession).order_by(ChatSession.query_timestamp.desc()).limit(limit).all()