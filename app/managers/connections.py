import asyncio
import json
import uuid
from typing import Dict, List

from fastapi.websockets import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "active_connections"):
            self.active_connections: Dict[uuid.UUID, List[WebSocket]] = {}
            self._lock = asyncio.Lock()

    async def connect(self, connection_id: uuid.UUID, websocket: WebSocket):
        async with self._lock:
            if connection_id not in self.active_connections:
                self.active_connections[connection_id] = []
            self.active_connections[connection_id].append(websocket)
        await websocket.accept()

    async def disconnect(self, connection_id: uuid.UUID, websocket: WebSocket):
        async with self._lock:
            connections = self.active_connections.get(connection_id)
            if connections and websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.active_connections[connection_id]

    async def send_to_user(self, user_id: uuid.UUID, message: dict):
        text = json.dumps(message, ensure_ascii=False)
        async with self._lock:
            for ws in self.active_connections.get(user_id, []):
                try:
                    await ws.send_text(text)
                except (WebSocketDisconnect, ConnectionResetError, RuntimeError, asyncio.CancelledError):
                    continue


ws_manager = ConnectionManager()


def get_ws_manager() -> ConnectionManager:
    return ws_manager
