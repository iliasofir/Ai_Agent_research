"""
Route Health Check
"""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import get_settings
import os

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifie l'état de santé de l'API et des services"""
    
    # Vérifier les API keys
    serper_available = bool(os.getenv("SERPER_API_KEY"))
    google_available = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    
    services_status = {
        "api": True,
        "crewai": True,  # Toujours disponible si le code est présent
        "serper": serper_available,
        "google_ai": google_available
    }
    
    return HealthResponse(
        status="healthy" if all(services_status.values()) else "degraded",
        version=settings.app_version,
        services=services_status
    )
