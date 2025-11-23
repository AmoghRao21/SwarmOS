from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Iterate over a copy to avoid modification during iteration issues
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, remove the dead connection
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

manager = ConnectionManager()