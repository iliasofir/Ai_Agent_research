"""
Modèles Pydantic pour l'API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResearchStatus(str, Enum):
    """Statut d'une recherche"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    """Requête pour lancer une recherche"""
    topic: str = Field(..., description="Sujet de recherche", min_length=3)


class ResearchResponse(BaseModel):
    """Réponse d'une recherche"""
    status: ResearchStatus = Field(..., description="Statut de la recherche")
    topic: str = Field(..., description="Sujet recherché")
    result: str = Field(..., description="Résultat de la recherche")
    created_at: datetime = Field(default_factory=datetime.now)
    message: str = Field(..., description="Message de statut")


class ResearchResult(BaseModel):
    """Résultat d'une recherche complétée"""
    status: ResearchStatus
    topic: str
    report: str = Field(..., description="Rapport généré en Markdown")
    summary_points: List[str] = Field(..., description="Points clés résumés")
    created_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = Field(None, description="Temps d'exécution en secondes")


class UploadResponse(BaseModel):
    """Réponse après upload de fichier"""
    filename: str
    file_path: str
    file_size: int
    message: str
    uploaded_at: datetime = Field(default_factory=datetime.now)


class WebSocketMessage(BaseModel):
    """Message WebSocket"""
    type: str = Field(..., description="Type de message: status, progress, result, error")
    data: Dict[str, Any] = Field(..., description="Données du message")
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, bool] = Field(
        default_factory=lambda: {
            "api": True,
            "crewai": False,
            "serper": False
        }
    )
