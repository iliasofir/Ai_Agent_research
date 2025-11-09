"""
Point d'entrée principal de l'application FastAPI
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH pour importer firstone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from app.config import get_settings
from app.api.routes import research, upload, health
from app.websocket_manager import manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print(f"🚀 Démarrage de {settings.app_name} v{settings.app_version}")
    
    # Créer les répertoires nécessaires
    settings.knowledge_dir.mkdir(exist_ok=True)
    settings.output_dir.mkdir(exist_ok=True)
    settings.upload_dir.mkdir(exist_ok=True)
    
    yield
    
    # Shutdown
    print("👋 Arrêt de l'application")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API Backend pour le système multi-agents de recherche accélérée",
    lifespan=lifespan
)

# Configuration CORS - AVANT les routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# WebSocket endpoint - DIRECTEMENT sur app
# ====================================
@app.websocket("/api/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """
    WebSocket endpoint for real-time research progress updates
    
    Connect to: ws://localhost:8000/api/ws/progress
    """
    print(f"🔌 WebSocket connection attempt from {websocket.client}")
    
    try:
        await manager.connect(websocket)
        print(f"✅ WebSocket connected. Total: {len(manager.active_connections)}")
        
        while True:
            try:
                data = await websocket.receive_text()
                print(f"📨 Received: {data}")
                
                if data == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": "now",
                        "connections": len(manager.active_connections)
                    })
                    
            except WebSocketDisconnect:
                print(f"🔌 Client disconnected")
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                break
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket)
        print(f"🔌 Cleanup complete. Remaining: {len(manager.active_connections)}")


# ====================================
# Inclure les routes REST
# ====================================
app.include_router(health.router, tags=["Health"])
app.include_router(
    research.router,
    prefix=f"{settings.api_prefix}/research",
    tags=["Research"]
)
app.include_router(
    upload.router,
    prefix=f"{settings.api_prefix}/upload",
    tags=["Upload"]
)
# NOTE: WebSocket is registered directly above, not through router


@app.get("/")
async def root():
    """Point d'entrée racine de l'API"""
    return JSONResponse(content={
        "message": f"Bienvenue sur {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "websocket": "/api/ws/progress"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )