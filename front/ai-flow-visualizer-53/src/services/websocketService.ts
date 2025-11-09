/**
 * Service WebSocket pour les mises à jour en temps réel de la recherche
 */

export type AgentType = "Researcher" | "Reviewer" | "Synthesizer" | "System";
export type AgentStatus = 
  | "started" 
  | "thinking" 
  | "working" 
  | "done" 
  | "error" 
  | "retry" 
  | "approved" 
  | "rejected"
  | "completed"
  | "connected"
  | "ping"
  | "pong";

// Le backend envoie directement les données à la racine du message
export interface WebSocketMessage {
  agent: AgentType;
  status: AgentStatus;
  message: string;
  timestamp: string;
  details?: Record<string, any>;
  iteration?: number;
}

export type WebSocketEventHandler = (message: WebSocketMessage) => void;

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/api/v1";

export class ResearchWebSocket {
  private ws: WebSocket | null = null;
  private researchId: string;
  private handlers: Set<WebSocketEventHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private keepaliveInterval: number | null = null;

  constructor(researchId: string) {
    this.researchId = researchId;
  }

  /**
   * Connecte au WebSocket
   */
connect(): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      const wsUrl = `ws://localhost:8000/api/ws/progress`;
      console.log("🔌 Connecting to WebSocket:", wsUrl);

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("✅ WebSocket connected for research:", this.researchId);
        this.reconnectAttempts = 0;
        
        // Démarrer le keepalive (ping toutes les 25 secondes)
        this.startKeepalive();
        
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Ignorer les messages de keepalive
          if (message.status === "ping" || message.status === "pong") {
            console.log("💓 Keepalive received");
            return;
          }
          
          console.log("📨 WebSocket message received:", message);
          this.handleMessage(message);
        } catch (error) {
          console.error("⚠️ Error parsing WebSocket message:", error);
        }
      };

      this.ws.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
        console.warn("⚠️ Connection attempt failed — check if FastAPI server is running.");
        reject(error);
      };

      this.ws.onclose = (event) => {
        this.stopKeepalive();
        
        if (event.wasClean) {
          console.log(`🔕 WebSocket closed cleanly (code=${event.code}, reason=${event.reason})`);
        } else {
          console.warn("⚠️ WebSocket closed unexpectedly (server down or connection lost)");
        }
        this.handleReconnect();
      };
    } catch (error) {
      console.error("🚫 Failed to create WebSocket connection:", error);
      reject(error);
    }
  });
}

  /**
   * Démarre le keepalive (ping régulier)
   */
  private startKeepalive() {
    this.stopKeepalive(); // Nettoyer l'ancien si existe
    
    this.keepaliveInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        try {
          this.ws.send("ping");
          console.log("💓 Ping sent");
        } catch (error) {
          console.error("❌ Error sending ping:", error);
        }
      }
    }, 25000); // Ping toutes les 25 secondes
  }

  /**
   * Arrête le keepalive
   */
  private stopKeepalive() {
    if (this.keepaliveInterval) {
      clearInterval(this.keepaliveInterval);
      this.keepaliveInterval = null;
    }
  }


  /**
   * Gère la reconnexion automatique
   */
  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect().catch((error) => {
          console.error("Reconnection failed:", error);
        });
      }, this.reconnectDelay);
    } else {
      console.error("Max reconnection attempts reached");
    }
  }

  /**
   * Gère les messages reçus
   */
  private handleMessage(message: WebSocketMessage) {
    console.log("📨 Received WebSocket message:", message);
    
    // Appelle tous les handlers enregistrés
    this.handlers.forEach((handler) => {
      try {
        handler(message);
      } catch (error) {
        console.error("❌ Error in WebSocket handler:", error);
      }
    });
  }

  /**
   * Enregistre un handler pour les messages
   */
  on(handler: WebSocketEventHandler) {
    console.log("Registering WebSocket handler");
    this.handlers.add(handler);
    console.log(`Total handlers:`, this.handlers.size);
  }

  /**
   * Désenregistre un handler
   */
  off(handler: WebSocketEventHandler) {
    this.handlers.delete(handler);
  }

  /**
   * Ferme la connexion WebSocket
   */
  disconnect() {
    this.stopKeepalive();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.handlers.clear();
  }

  /**
   * Vérifie si le WebSocket est connecté
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

/**
 * Crée une connexion WebSocket pour une recherche
 */
export const createResearchWebSocket = (researchId: string): ResearchWebSocket => {
  return new ResearchWebSocket(researchId);
};
