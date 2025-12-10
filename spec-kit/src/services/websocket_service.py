import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from src.services.rag_service import rag_service, RAGResponse


class ConnectionManager:
    """Manage WebSocket connections for real-time chat functionality."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        """Add a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": asyncio.get_event_loop().time()
        }
        self.logger.info(f"New WebSocket connection from user: {user_id}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        self.logger.info("WebSocket connection closed")

    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.add(connection)

        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)


# Global connection manager instance
manager = ConnectionManager()


async def handle_websocket_message(websocket: WebSocket, data: str):
    """
    Handle incoming WebSocket messages and process them.

    Expected message format:
    {
        "type": "chat_message",
        "query": "user query",
        "context_type": "full_book|selected_text",
        "selected_text": "optional selected text",
        "user_id": "optional user id"
    }
    """
    try:
        message_data = json.loads(data)
        message_type = message_data.get("type")

        if message_type == "chat_message":
            query = message_data.get("query")
            context_type = message_data.get("context_type", "full_book")
            selected_text = message_data.get("selected_text")
            user_id = message_data.get("user_id")

            if not query:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "error",
                        "message": "Query is required"
                    }),
                    websocket
                )
                return

            # Send typing indicator
            await manager.send_personal_message(
                json.dumps({
                    "type": "typing",
                    "status": True
                }),
                websocket
            )

            try:
                # Process the query based on context type
                if context_type == "full_book":
                    rag_response: RAGResponse = await rag_service.process_full_book_query(
                        query=query,
                        user_id=user_id
                    )
                elif context_type == "selected_text":
                    if not selected_text:
                        raise ValueError("selected_text is required for selected_text context_type")

                    rag_response: RAGResponse = await rag_service.process_selected_text_query(
                        query=query,
                        selected_text=selected_text,
                        user_id=user_id
                    )
                else:
                    raise ValueError(f"Invalid context_type: {context_type}")

                # Format the response
                formatted_response = rag_service.format_response(rag_response)

                # Send the response
                response_message = {
                    "type": "chat_response",
                    "response": formatted_response,
                    "original_query": query
                }

                await manager.send_personal_message(
                    json.dumps(response_message),
                    websocket
                )

            except Exception as e:
                error_message = {
                    "type": "error",
                    "message": f"Error processing query: {str(e)}"
                }
                await manager.send_personal_message(
                    json.dumps(error_message),
                    websocket
                )

            finally:
                # Send typing indicator off
                await manager.send_personal_message(
                    json.dumps({
                        "type": "typing",
                        "status": False
                    }),
                    websocket
                )

        elif message_type == "ping":
            # Respond to ping messages
            await manager.send_personal_message(
                json.dumps({
                    "type": "pong"
                }),
                websocket
            )

        else:
            # Unknown message type
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }),
                websocket
            )

    except json.JSONDecodeError:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": "Invalid JSON format"
            }),
            websocket
        )
    except Exception as e:
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "message": f"Server error: {str(e)}"
            }),
            websocket
        )