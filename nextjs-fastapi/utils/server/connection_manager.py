from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        print("ConnectionManager initialized")
        self.active_connections: Dict[str, WebSocket] = {}

    def connect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    def check_connection(self, user_id: str):
        return user_id in self.active_connections
    
manager = ConnectionManager()
