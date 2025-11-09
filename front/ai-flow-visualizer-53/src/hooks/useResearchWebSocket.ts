import { useEffect, useRef, useCallback } from "react";
import {
  ResearchWebSocket,
  createResearchWebSocket,
  WebSocketMessage,
  WebSocketEventHandler,
} from "@/services/websocketService";

interface UseResearchWebSocketOptions {
  researchId: string | null;
  onMessage?: (message: WebSocketMessage) => void;
  autoConnect?: boolean;
}

export const useResearchWebSocket = ({
  researchId,
  onMessage,
  autoConnect = true,
}: UseResearchWebSocketOptions) => {
  const wsRef = useRef<ResearchWebSocket | null>(null);
  const handlersRef = useRef<Set<WebSocketEventHandler>>(new Set());

  /**
   * Connecte au WebSocket
   */
  const connect = useCallback(async () => {
    if (wsRef.current?.isConnected()) {
      console.log("Already connected");
      return;
    }

    try {
      const ws = createResearchWebSocket(researchId || "default");
      
      // Enregistre le handler général si fourni
      if (onMessage) {
        ws.on(onMessage);
      }

      // Enregistre tous les handlers existants
      handlersRef.current.forEach((handler) => {
        ws.on(handler);
      });

      await ws.connect();
      wsRef.current = ws;
      console.log("WebSocket connected successfully");
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
    }
  }, [researchId, onMessage]);

  /**
   * Déconnecte le WebSocket
   */
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
  }, []);

  /**
   * Enregistre un handler pour les messages
   */
  const on = useCallback((handler: WebSocketEventHandler) => {
    handlersRef.current.add(handler);

    // Si déjà connecté, enregistre aussi sur l'instance WebSocket
    if (wsRef.current) {
      wsRef.current.on(handler);
    }
  }, []);

  /**
   * Désenregistre un handler
   */
  const off = useCallback((handler: WebSocketEventHandler) => {
    handlersRef.current.delete(handler);

    if (wsRef.current) {
      wsRef.current.off(handler);
    }
  }, []);

  /**
   * Vérifie si connecté
   */
  const isConnected = useCallback(() => {
    return wsRef.current?.isConnected() ?? false;
  }, []);

  // Auto-connect si demandé
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [researchId, autoConnect, connect, disconnect]);

  return {
    connect,
    disconnect,
    on,
    off,
    isConnected,
  };
};
