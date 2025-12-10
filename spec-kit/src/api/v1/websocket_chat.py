from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from typing import Optional

from src.services.websocket_service import manager, handle_websocket_message


router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time chat communication.

    Args:
        websocket: WebSocket connection
        user_id: User identifier for the connection
    """
    await manager.connect(websocket, user_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # Handle the message
            await handle_websocket_message(websocket, data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")


@router.websocket("/ws/anonymous")
async def websocket_anonymous_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for anonymous real-time chat communication.

    Args:
        websocket: WebSocket connection
    """
    await manager.connect(websocket, user_id=None)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # Handle the message
            await handle_websocket_message(websocket, data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")


# Add the WebSocket router to the main app in main.py
# This endpoint should be registered with the main FastAPI app