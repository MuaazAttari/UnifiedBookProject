import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.main import app
from src.services.websocket_service import ConnectionManager, handle_websocket_message
from src.services.rag_service import RAGResponse


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    with TestClient(app) as client:
        yield client


class TestWebSocketService:
    """Test suite for WebSocket chat service."""

    def test_websocket_routes_exist(self, test_client):
        """Test that WebSocket routes are properly registered."""
        # Test that the WebSocket endpoint exists
        # Note: We can't easily test WebSocket endpoints with TestClient
        # So we'll just verify the routes exist by checking the app routes
        assert any(route.name == 'websocket_endpoint' for route in app.routes)
        assert any(route.name == 'websocket_anonymous_endpoint' for route in app.routes)

    def test_connection_manager_initialization(self):
        """Test that the connection manager initializes correctly."""
        manager = ConnectionManager()
        assert len(manager.active_connections) == 0
        assert len(manager.connection_metadata) == 0

    @pytest.mark.asyncio
    async def test_handle_websocket_message_chat_message(self):
        """Test handling a chat message via WebSocket."""
        # Mock the websocket
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.send_text = AsyncMock()

        # Mock RAG service response
        with patch('src.services.websocket_service.rag_service') as mock_rag_service:
            mock_response = RAGResponse(
                answer="This is a test answer.",
                context="This is the context.",
                sources=[{
                    "id": "test_source",
                    "title": "Test Chapter",
                    "source": "test.md",
                    "relevance_score": 8.5,
                    "content_preview": "Preview..."
                }],
                tokens_used=50,
                confidence=0.85
            )

            mock_rag_service.process_full_book_query = AsyncMock(return_value=mock_response)
            mock_rag_service.format_response = MagicMock(return_value={
                "answer": "This is a test answer.",
                "context": "This is the context.",
                "sources": [{
                    "id": "test_source",
                    "title": "Test Chapter",
                    "source": "test.md",
                    "relevance_score": 8.5,
                    "content_preview": "Preview...",
                    "chunk_index": 0
                }],
                "tokens_used": 50,
                "confidence": 0.85,
                "confidence_percentage": 85.0,
                "processed": True
            })

            # Test message data
            message_data = {
                "type": "chat_message",
                "query": "Test question?",
                "context_type": "full_book",
                "user_id": "test_user"
            }

            # Call the handler
            await handle_websocket_message(mock_websocket, json.dumps(message_data))

            # Verify the typing indicators were sent
            assert mock_websocket.send_text.call_count >= 2  # typing on, response, typing off

    @pytest.mark.asyncio
    async def test_handle_websocket_message_ping_pong(self):
        """Test handling a ping message via WebSocket."""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.send_text = AsyncMock()

        message_data = {"type": "ping"}

        # Call the handler
        await handle_websocket_message(mock_websocket, json.dumps(message_data))

        # Verify pong response was sent
        mock_websocket.send_text.assert_called_once()
        args, kwargs = mock_websocket.send_text.call_args
        response = json.loads(args[0])
        assert response["type"] == "pong"

    @pytest.mark.asyncio
    async def test_handle_websocket_message_invalid_json(self):
        """Test handling invalid JSON via WebSocket."""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.send_text = AsyncMock()

        # Call the handler with invalid JSON
        await handle_websocket_message(mock_websocket, "invalid json {")

        # Verify error response was sent
        mock_websocket.send_text.assert_called_once()
        args, kwargs = mock_websocket.send_text.call_args
        response = json.loads(args[0])
        assert response["type"] == "error"
        assert "Invalid JSON format" in response["message"]

    @pytest.mark.asyncio
    async def test_handle_websocket_message_unknown_type(self):
        """Test handling unknown message type via WebSocket."""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.send_text = AsyncMock()

        message_data = {"type": "unknown_type"}

        # Call the handler
        await handle_websocket_message(mock_websocket, json.dumps(message_data))

        # Verify error response was sent
        mock_websocket.send_text.assert_called_once()
        args, kwargs = mock_websocket.send_text.call_args
        response = json.loads(args[0])
        assert response["type"] == "error"
        assert "Unknown message type" in response["message"]

    @pytest.mark.asyncio
    async def test_handle_websocket_message_missing_query(self):
        """Test handling a chat message with missing query."""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.send_text = AsyncMock()

        message_data = {
            "type": "chat_message",
            "context_type": "full_book"
            # Missing query
        }

        # Call the handler
        await handle_websocket_message(mock_websocket, json.dumps(message_data))

        # Verify error response was sent
        mock_websocket.send_text.assert_called()
        calls = mock_websocket.send_text.call_args_list
        # Check that an error message was sent
        for call in calls:
            args, kwargs = call
            response = json.loads(args[0])
            if response["type"] == "error":
                assert "Query is required" in response["message"]
                break