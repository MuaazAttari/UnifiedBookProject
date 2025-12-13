"""
Tests for RAG API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.database.session import SessionLocal, engine
from src.models.user import Base
from unittest.mock import patch, AsyncMock


# Create a test client
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_test_db():
    """Setup test database"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield

    # Cleanup - drop all tables
    Base.metadata.drop_all(bind=engine)


def test_ingest_endpoint(setup_test_db):
    """Test the ingest endpoint"""
    # Mock the rag service
    with patch('src.api.v1.rag.rag_service') as mock_rag_service:
        mock_rag_service.ingest_document = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/ingest",
            json={
                "doc_id": "test_doc",
                "markdown": "Test content",
                "metadata": {"source": "test"}
            },
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200


def test_query_endpoint():
    """Test the query endpoint"""
    with patch('src.api.v1.rag.rag_service') as mock_rag_service:
        mock_rag_service.query = AsyncMock(return_value=[])

        response = client.post(
            "/api/v1/query",
            json={
                "text": "test query"
            }
        )

        assert response.status_code == 200


def test_create_session_endpoint(setup_test_db):
    """Test the session creation endpoint"""
    with patch('src.api.v1.rag.rag_service') as mock_rag_service:
        from src.rag_chat.models import ChatSession
        mock_session = ChatSession(id="test_session_id")
        mock_rag_service.create_session = lambda db, user_id: mock_session

        response = client.post(
            "/api/v1/session",
            json={},
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}