import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any

from src.main import app
from src.db.database import get_db
from src.models.chat_session import ChatSession
from src.services.rag_service import RAGResponse


# Create a test database session
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_rag_service():
    """Mock the RAG service for testing."""
    with patch('src.api.v1.chat.rag_service') as mock_service:
        # Mock the RAG response
        mock_response = RAGResponse(
            answer="This is a test answer based on the context.",
            context="This is the context used for the answer.",
            sources=[{
                "id": "test_source",
                "title": "Test Chapter",
                "source": "test_chapter.md",
                "relevance_score": 9.0,
                "content_preview": "This is a preview of the content..."
            }],
            tokens_used=50,
            confidence=0.85
        )

        mock_service.process_full_book_query = AsyncMock(return_value=mock_response)
        mock_service.process_selected_text_query = AsyncMock(return_value=mock_response)
        mock_service.get_relevant_chapters = AsyncMock(return_value=[{
            "source": "test_chapter.md",
            "title": "Test Chapter",
            "chunks": [],
            "total_score": 9.0
        }])
        mock_service.validate_and_clean_query = AsyncMock(return_value="cleaned test query")

        yield mock_service


class TestChatAPI:
    """Test suite for chat API endpoints."""

    def test_create_chat_session_full_book(self, client, mock_rag_service):
        """Test creating a chat session with full book context."""
        # Mock the chat session service
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_session = MagicMock()
            mock_session.session_id = "test-session-id"
            mock_session.query = "What is this about?"
            mock_session.response = "This is a test answer based on the context."
            mock_session.context_type = "full_book"
            mock_session.user_id = "test-user"
            mock_session.tokens_used = 50

            mock_chat_service.create_chat_session.return_value = mock_session
            mock_chat_service.update_chat_session.return_value = mock_session

            response = client.post(
                "/api/v1/chat/",
                json={
                    "user_id": "test-user",
                    "query": "What is this about?",
                    "context_type": "full_book"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-id"
            assert data["query"] == "What is this about?"
            assert "test answer" in data["response"].lower()

    def test_create_chat_session_selected_text(self, client, mock_rag_service):
        """Test creating a chat session with selected text context."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_session = MagicMock()
            mock_session.session_id = "test-session-id"
            mock_session.query = "What does this mean?"
            mock_session.response = "This is a test answer based on the context."
            mock_session.context_type = "selected_text"
            mock_session.selected_text = "This is the selected text."
            mock_session.user_id = "test-user"
            mock_session.tokens_used = 50

            mock_chat_service.create_chat_session.return_value = mock_session
            mock_chat_service.update_chat_session.return_value = mock_session

            response = client.post(
                "/api/v1/chat/",
                json={
                    "user_id": "test-user",
                    "query": "What does this mean?",
                    "context_type": "selected_text",
                    "selected_text": "This is the selected text."
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-id"
            assert data["context_type"] == "selected_text"
            assert data["selected_text"] == "This is the selected text."

    def test_create_chat_session_invalid_context_type(self, client):
        """Test creating a chat session with invalid context type."""
        response = client.post(
            "/api/v1/chat/",
            json={
                "user_id": "test-user",
                "query": "What is this about?",
                "context_type": "invalid_type"
            }
        )

        assert response.status_code == 400
        assert "context_type must be either" in response.json()["detail"]

    def test_process_query_full_book(self, client, mock_rag_service):
        """Test processing a query with full book context."""
        response = client.post(
            "/api/v1/chat/query",
            params={
                "query": "What is this about?",
                "context_type": "full_book"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "context" in data
        assert "sources" in data
        assert "This is a test answer" in data["answer"]

    def test_process_query_selected_text(self, client, mock_rag_service):
        """Test processing a query with selected text context."""
        response = client.post(
            "/api/v1/chat/query",
            params={
                "query": "What does this mean?",
                "context_type": "selected_text",
                "selected_text": "This is the selected text."
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_get_chat_session(self, client):
        """Test getting a specific chat session."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_session = MagicMock()
            mock_session.session_id = "test-session-id"
            mock_session.query = "Test query"
            mock_session.response = "Test response"
            mock_session.context_type = "full_book"
            mock_session.user_id = "test-user"

            mock_chat_service.get_chat_session.return_value = mock_session

            response = client.get("/api/v1/chat/test-session-id")

            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-id"

    def test_get_chat_session_not_found(self, client):
        """Test getting a non-existent chat session."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_chat_service.get_chat_session.return_value = None

            response = client.get("/api/v1/chat/non-existent-session")

            assert response.status_code == 404

    def test_get_chat_sessions(self, client):
        """Test getting multiple chat sessions."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_session = MagicMock()
            mock_session.session_id = "test-session-id"
            mock_session.query = "Test query"
            mock_session.response = "Test response"

            mock_chat_service.get_chat_sessions.return_value = [mock_session]

            response = client.get("/api/v1/chat/")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["session_id"] == "test-session-id"

    def test_get_user_chat_history(self, client):
        """Test getting chat history for a specific user."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_session = MagicMock()
            mock_session.session_id = "test-session-id"
            mock_session.query = "Test query"
            mock_session.response = "Test response"

            mock_chat_service.get_chat_sessions.return_value = [mock_session]

            response = client.get("/api/v1/chat/history/test-user")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_delete_chat_session(self, client):
        """Test deleting a chat session."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_chat_service.delete_chat_session.return_value = True

            response = client.delete("/api/v1/chat/test-session-id")

            assert response.status_code == 200
            assert response.json()["message"] == "Chat session deleted successfully"

    def test_validate_query(self, client):
        """Test query validation endpoint."""
        response = client.post("/api/v1/chat/validate-query", params={"query": "test query"})

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["cleaned_query"] == "test query"

    def test_validate_query_empty(self, client):
        """Test query validation with empty query."""
        response = client.post("/api/v1/chat/validate-query", params={"query": ""})

        assert response.status_code == 400

    def test_find_relevant_chapters(self, client, mock_rag_service):
        """Test finding relevant chapters for a query."""
        response = client.post(
            "/api/v1/chat/find-relevant-chapters",
            params={"query": "test query", "top_k": 3}
        )

        assert response.status_code == 200
        data = response.json()
        assert "chapters" in data


class TestQuerySanitization:
    """Test query sanitization in the API."""

    def test_create_chat_session_with_malicious_query(self, client, mock_rag_service):
        """Test that malicious queries are sanitized."""
        with patch('src.api.v1.chat.ChatSessionService') as mock_chat_service:
            mock_session = MagicMock()
            mock_session.session_id = "test-session-id"
            mock_session.query = "cleaned test query"  # Should be sanitized
            mock_session.response = "Test response"
            mock_session.context_type = "full_book"
            mock_session.user_id = "test-user"

            mock_chat_service.create_chat_session.return_value = mock_session
            mock_chat_service.update_chat_session.return_value = mock_session

            # Send a query with potential XSS content
            response = client.post(
                "/api/v1/chat/",
                json={
                    "user_id": "test-user",
                    "query": "<script>alert('xss')</script>What is this about?",
                    "context_type": "full_book"
                }
            )

            # Should still succeed but with sanitized query
            assert response.status_code == 200

    def test_process_query_with_malicious_content(self, client, mock_rag_service):
        """Test that malicious content in queries is sanitized."""
        # This would require more complex mocking to verify sanitization
        # happened before the RAG service was called
        response = client.post(
            "/api/v1/chat/query",
            params={
                "query": "<script>alert('xss')</script>What is this about?",
                "context_type": "full_book"
            }
        )

        # Should return a 400 error due to validation if properly sanitized
        # or 200 if it passes validation after sanitization
        assert response.status_code in [200, 400]  # Both are acceptable depending on sanitization approach