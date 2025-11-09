/**
 * Service pour gérer les requêtes de recherche
 */

export interface ResearchRequest {
  topic: string;
}

export enum ResearchStatus {
  SUCCESS = "success",
  FAILED = "failed",
  PROCESSING = "processing",
  STARTED = "started",
  COMPLETED = "completed"
}


export interface ResearchResponse {
  status: ResearchStatus;
  topic: string;
  result: string;
  message: string;
  research_id?: string; // ID pour la connexion WebSocket
}



export interface PDFUploadResponse {
  status: string;
  message: string;
  file_id: string;
  file_path: string;
  filename: string;
  topic?: string;
  page_count?: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";





/**
 * Upload un fichier PDF
 * @param file - Le fichier PDF à uploader
 * @param topic - Le sujet de recherche (optionnel)
 * @returns La réponse de l'API avec le file_id
 */
export const uploadPDF = async (file: File, topic?: string): Promise<PDFUploadResponse> => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    if (topic) {
      formData.append("topic", topic);
    }

    const response = await fetch(`${API_BASE_URL}/research/upload-pdf`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erreur lors de l'upload du PDF:", error);
    throw error;
  }
};

/**
 * Envoie une requête de recherche avec des PDFs
 * @param topic - Le sujet de recherche
 * @param fileIds - Les IDs des fichiers PDF uploadés
 * @returns La réponse de l'API
 */
export const sendResearchWithPDFs = async (
  topic: string,
  fileIds: string[]
): Promise<ResearchResponse> => {
  try {
    const params = new URLSearchParams({
      topic,
    });
    
    // Ajouter les file_ids
    fileIds.forEach(id => params.append("file_ids", id));

    const response = await fetch(`${API_BASE_URL}/research/send-with-pdfs?${params}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erreur lors de l'envoi de la requête de recherche avec PDFs:", error);
    throw error;
  }
};


/**
 * Envoie une requête de recherche à l'API
 * @param topic - Le sujet de recherche
 * @returns La réponse de l'API
 */
export const sendResearchRequest = async (topic: string): Promise<ResearchResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/research/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ topic }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erreur lors de l'envoi de la requête de recherche:", error);
    throw error;
  }
};
