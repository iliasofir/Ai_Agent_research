# app/websocket_manager.py
from fastapi import WebSocket
from typing import List, Dict, Any
import asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"✅ WebSocket client connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"❌ WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def send_progress(self, message: Dict[str, Any]):
        """Send progress update to all connected clients"""
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        disconnected = []
        async with self._lock:
            connections_copy = self.active_connections.copy()
        
        for connection in connections_copy:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"⚠️ Error sending to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            await self.disconnect(conn)

    async def broadcast(self, agent: str, status: str, message: str = "", details: Dict = None, iteration: int = None):
        """Broadcast agent progress with structured data"""
        payload = {
            "agent": agent,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            payload["details"] = details
        
        if iteration is not None:
            payload["iteration"] = iteration
        
        await self.send_progress(payload)
        
        # Console logging
        icon = {
            "started": "🚀",
            "thinking": "🤔",
            "working": "⚙️",
            "done": "✅",
            "error": "❌",
            "retry": "🔄",
            "approved": "✓",
            "rejected": "✗"
        }.get(status, "📡")
        
        print(f"{icon} [{agent}] {status.upper()}: {message}")

# Global manager instance
manager = ConnectionManager()