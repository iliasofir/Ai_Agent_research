"""
Configuration de l'application FastAPI
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Application
    app_name: str = "Multi-Agent Research System API"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # API
    api_prefix: str = "/api/v1"
    
    # CORS
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # API Keys (depuis .env)
    model: str = ""  # Modèle LLM utilisé (ex: gemini/gemini-2.5-flash)
    serper_api_key: str = ""
    google_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    
    # Chemins du projet
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    knowledge_dir: Path = base_dir / "knowledge"
    output_dir: Path = base_dir / "output"
    upload_dir: Path = knowledge_dir / "uploaded_pdfs"
    
    # WebSocket
    ws_heartbeat_interval: int = 30
    
    # CrewAI
    crew_verbose: bool = True
    
    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retourne les paramètres de configuration (cached)"""
    return Settings()
