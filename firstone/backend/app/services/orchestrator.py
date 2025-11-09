"""
Service d'orchestration des agents CrewAI
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))

from firstone.crew import Firstone
from app.config import get_settings

settings = get_settings()


class OrchestratorService:
    """Service pour orchestrer les agents CrewAI"""
    
    def __init__(self):
        self.active_researches: Dict[str, Dict[str, Any]] = {}
    
    async def run_research(
        self,
        research_id: str,
        topic: str,
        year: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Lance une recherche avec CrewAI
        
        Args:
            research_id: ID unique de la recherche
            topic: Sujet de recherche
            year: Année ciblée (optionnel)
            preferences: Préférences utilisateur (optionnel)
            
        Returns:
            Résultats de la recherche
        """
        try:
            # Préparer les inputs pour CrewAI
            inputs = {
                'topic': topic,
                'current_year': str(year or datetime.now().year)
            }
            
            # Marquer la recherche comme active
            self.active_researches[research_id] = {
                'status': 'running',
                'started_at': datetime.now(),
                'topic': topic
            }
            
            # Exécuter CrewAI dans un thread séparé pour ne pas bloquer
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._run_crew_sync,
                inputs
            )
            
            # Lire le rapport généré
            report_path = settings.output_dir / "report.md"
            report_content = ""
            if report_path.exists():
                report_content = report_path.read_text(encoding='utf-8')
            
            # Mettre à jour le statut
            self.active_researches[research_id]['status'] = 'completed'
            self.active_researches[research_id]['completed_at'] = datetime.now()
            
            return {
                'research_id': research_id,
                'status': 'completed',
                'topic': topic,
                'report': report_content,
                'raw_result': str(result),
                'completed_at': datetime.now()
            }
            
        except Exception as e:
            # En cas d'erreur
            self.active_researches[research_id]['status'] = 'failed'
            self.active_researches[research_id]['error'] = str(e)
            
            raise Exception(f"Erreur lors de l'exécution de la recherche: {str(e)}")
    
    def _run_crew_sync(self, inputs: Dict[str, Any]) -> Any:
        """Exécute CrewAI de manière synchrone"""
        crew_instance = Firstone()
        return crew_instance.crew().kickoff(inputs=inputs)
    
    def get_research_status(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une recherche"""
        return self.active_researches.get(research_id)
    
    def list_active_researches(self) -> Dict[str, Dict[str, Any]]:
        """Liste toutes les recherches actives"""
        return self.active_researches


# Instance singleton
orchestrator_service = OrchestratorService()
