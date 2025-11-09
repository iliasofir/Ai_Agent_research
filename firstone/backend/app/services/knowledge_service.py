"""
Service de gestion des connaissances (Knowledge Ingestion)
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiofiles
from datetime import datetime

from app.config import get_settings

settings = get_settings()


class KnowledgeService:
    """Service pour gérer l'ingestion de documents"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.docx', '.doc'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    async def save_uploaded_file(
        self,
        filename: str,
        content: bytes
    ) -> Dict[str, Any]:
        """
        Sauvegarde un fichier uploadé
        
        Args:
            filename: Nom du fichier
            content: Contenu du fichier en bytes
            
        Returns:
            Informations sur le fichier sauvegardé
        """
        # Vérifier l'extension
        file_path = Path(filename)
        if file_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Extension non autorisée. Extensions acceptées: {self.ALLOWED_EXTENSIONS}"
            )
        
        # Vérifier la taille
        if len(content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"Fichier trop volumineux. Taille max: {self.MAX_FILE_SIZE / (1024*1024)} MB"
            )
        
        # Créer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        save_path = settings.upload_dir / unique_filename
        
        # Sauvegarder le fichier
        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(content)
        
        return {
            'filename': unique_filename,
            'original_filename': filename,
            'file_path': str(save_path),
            'file_size': len(content),
            'uploaded_at': datetime.now()
        }
    
    async def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """Liste tous les fichiers uploadés"""
        files = []
        
        for file_path in settings.upload_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.ALLOWED_EXTENSIONS:
                stat = file_path.stat()
                files.append({
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'file_size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime)
                })
        
        return files
    
    async def delete_file(self, filename: str) -> bool:
        """Supprime un fichier uploadé"""
        file_path = settings.upload_dir / filename
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        
        return False


# Instance singleton
knowledge_service = KnowledgeService()
