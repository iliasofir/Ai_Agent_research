"""
WebSocket routes for real-time progress updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager
import asyncio

# Create router WITHOUT prefix - we'll add it in main.py
router = APIRouter()


@router.websocket("/progress")
async def websocket_progress(websocket: WebSocket):
    """
    WebSocket endpoint for real-time research progress updates
    
    Endpoint: ws://localhost:8000/api/ws/progress
    """
    print(f"🔌 WebSocket connection attempt from {websocket.client}")
    
    try:
        await manager.connect(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(manager.active_connections)}")
        
        # Envoyer un message de bienvenue
        await websocket.send_json({
            "agent": "System",
            "status": "connected",
            "message": "WebSocket connected successfully",
            "timestamp": "now"
        })
        
        # Keepalive task
        async def send_keepalive():
            while True:
                try:
                    await asyncio.sleep(30)  # Ping toutes les 30 secondes
                    await websocket.send_json({
                        "agent": "System",
                        "status": "ping",
                        "message": "keepalive",
                        "timestamp": "now"
                    })
                except:
                    break
        
        keepalive_task = asyncio.create_task(send_keepalive())
        
        try:
            while True:
                # Attendre les messages du client (non bloquant)
                data = await websocket.receive_text()
                print(f"📨 Received from client: {data}")
                
                # Répondre aux pings
                if data == "ping":
                    await websocket.send_json({
                        "agent": "System",
                        "status": "pong",
                        "message": "pong",
                        "timestamp": "now",
                        "connections": len(manager.active_connections)
                    })
                    
        except WebSocketDisconnect:
            print(f"🔌 Client disconnected normally")
        except Exception as e:
            print(f"⚠️ Error in WebSocket message loop: {e}")
        finally:
            keepalive_task.cancel()
                
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        
    finally:
        await manager.disconnect(websocket)
        print(f"🔌 Cleanup complete. Remaining: {len(manager.active_connections)}")