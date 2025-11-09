"""
Routes d'upload de fichiers
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from app.models.schemas import UploadResponse
from app.services.knowledge_service import knowledge_service

router = APIRouter()


@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload un document (PDF, TXT, MD, DOCX) dans la base de connaissances
    
    Le fichier sera utilisé par les agents pour enrichir leurs recherches.
    """
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Sauvegarder le fichier
        result = await knowledge_service.save_uploaded_file(
            filename=file.filename,
            content=content
        )
        
        return UploadResponse(
            filename=result['filename'],
            file_path=result['file_path'],
            file_size=result['file_size'],
            message=f"Fichier '{file.filename}' uploadé avec succès",
            uploaded_at=result['uploaded_at']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )


@router.get("/files")
async def list_files():
    """Liste tous les fichiers uploadés dans la base de connaissances"""
    try:
        files = await knowledge_service.list_uploaded_files()
        return {
            "total": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des fichiers: {str(e)}"
        )


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Supprime un fichier uploadé"""
    try:
        deleted = await knowledge_service.delete_file(filename)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Fichier '{filename}' non trouvé"
            )
        
        return {"message": f"Fichier '{filename}' supprimé avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )
