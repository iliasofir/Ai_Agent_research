import { useState, useEffect, useCallback } from "react";
import { AgentNode } from "./AgentNode";
import { FlowArrow } from "./FlowArrow";
import { Check, RotateCcw } from "lucide-react";
import { useResearchWebSocket } from "@/hooks/useResearchWebSocket";
import {
  WebSocketMessage,
  AgentType,
  AgentStatus,
} from "@/services/websocketService";
import { useToast } from "@/hooks/use-toast";

interface WorkflowAnimationProps {
  onComplete: (report: string) => void;
  topic?: string;
  researchId: string | null;
}

type LocalAgentStatus = "idle" | "thinking" | "approved" | "rejected";

interface AgentState {
  status: LocalAgentStatus;
  message: string;
}

export const WorkflowAnimation = ({
  onComplete,
  topic,
  researchId,
}: WorkflowAnimationProps) => {
  const { toast } = useToast();
  const [iteration, setIteration] = useState(1);
  const [stage, setStage] = useState<
    | "researcher"
    | "review-decision"
    | "rejected"
    | "approved"
    | "synthesizer"
    | "complete"
  >("researcher");

  const [agentStates, setAgentStates] = useState<{
    Researcher: AgentState;
    Reviewer: AgentState;
    Synthesizer: AgentState;
  }>({
    Researcher: {
      status: "idle",
      message: "En attente...",
    },
    Reviewer: { status: "idle", message: "En attente..." },
    Synthesizer: { status: "idle", message: "En attente..." },
  });

  // Gestion des messages WebSocket
  const handleWebSocketMessage = useCallback(
    (message: WebSocketMessage) => {
      console.log("📨 WebSocket message reçu:", message);

      const { agent, status, message: msg, details, iteration: iter } = message;

      // Mise à jour de l'itération si fournie
      if (iter) {
        setIteration(iter);
      }

      // Mapper le statut WebSocket vers le statut local
      let localStatus: LocalAgentStatus = "idle";

      if (
        status === "thinking" ||
        status === "working" ||
        status === "started"
      ) {
        localStatus = "thinking";
      } else if (
        status === "done" ||
        status === "approved" ||
        status === "completed"
      ) {
        localStatus = "approved";
      } else if (status === "rejected" || status === "retry") {
        localStatus = "rejected";
      }

      // Mise à jour de l'état de l'agent
      if (
        agent === "Researcher" ||
        agent === "Reviewer" ||
        agent === "Synthesizer"
      ) {
        setAgentStates((prev) => ({
          ...prev,
          [agent]: {
            status: localStatus,
            message: msg || prev[agent].message,
          },
        }));

        // Gestion des transitions de stage
        if (agent === "Researcher") {
          if (status === "done") {
            setStage("review-decision");
          }
        } else if (agent === "Reviewer") {
          if (status === "thinking" || status === "working") {
            setStage("review-decision");
          } else if (status === "done" && localStatus === "approved") {
            setStage("approved");
            setTimeout(() => setStage("synthesizer"), 1000);
          } else if (status === "retry" || status === "rejected") {
            setStage("rejected");
            setTimeout(() => setStage("researcher"), 2000);
          }
        } else if (agent === "Synthesizer") {
          if (status === "thinking" || status === "working") {
            setStage("synthesizer");
          } else if (status === "done" || status === "completed") {
            setStage("complete");
          }
        }
      }

      // Gestion des messages système
      if (agent === "System") {
        if (status === "completed") {
          setStage("complete");

          // Le rapport peut être dans details.final_report
          const finalReport =
            details?.final_report || details?.report_content || "";

          if (finalReport) {
            console.log("📄 Rapport reçu, longueur:", finalReport.length);
            onComplete(finalReport);
          } else {
            console.warn("⚠️ Aucun rapport trouvé dans les détails");
            // Essayer de charger le rapport depuis le fichier
            loadReportFromFile();
          }
        } else if (status === "error") {
          toast({
            title: "Erreur",
            description: msg,
            variant: "destructive",
          });
        }
      }

      // Gestion du rapport depuis le Synthesizer
      if (agent === "Synthesizer" && status === "done") {
        const reportContent = details?.report_content || "";
        if (reportContent) {
          console.log(
            "📄 Rapport reçu du Synthesizer, longueur:",
            reportContent.length
          );
          onComplete(reportContent);
        }
      }
    },
    [onComplete, toast]
  );

  // Fonction pour charger le rapport depuis le fichier si nécessaire
  const loadReportFromFile = async () => {
    try {
      const response = await fetch("/output/synthesis_report.md");
      if (response.ok) {
        const reportText = await response.text();
        console.log("📄 Rapport chargé depuis le fichier");
        onComplete(reportText);
      }
    } catch (error) {
      console.error("❌ Erreur lors du chargement du rapport:", error);
    }
  };

  useEffect(() => {
    if (stage === "complete") {
      toast({
        title: "✅ Recherche terminée!",
        description: "Votre rapport complet est disponible.",
      });
    } else if (stage === "rejected") {
      toast({
        title: "🔄 Amélioration en cours...",
        description: `Nouvelle tentative (${iteration}/3)`,
        variant: "default",
      });
    }
  }, [stage, iteration, toast]);

  // Connexion WebSocket
  useResearchWebSocket({
    researchId,
    onMessage: handleWebSocketMessage,
    autoConnect: true,
  });

  return (
    <div className="w-full max-w-7xl mx-auto py-12 animate-fade-in">
      {/* Topic Display */}
      {topic && (
        <div className="text-center mb-8">
          <div className="inline-block bg-primary/10 backdrop-blur-sm border border-primary/30 rounded-2xl px-6 py-3">
            <p className="text-sm text-muted-foreground mb-1">
              Recherche en cours pour
            </p>
            <p className="text-xl font-semibold text-foreground">{topic}</p>
            {iteration > 0 && (
              <p className="text-sm text-muted-foreground mt-2">
                Itération {iteration}/3
              </p>
            )}
          </div>
        </div>
      )}

      {/* Horizontal Layout Container */}
      <div className="relative">
        {/* Main Workflow Row */}
        <div className="flex items-center justify-center gap-8 px-4">
          {/* Agent 1: Researcher */}
          <div className="flex-shrink-0">
            <AgentNode
              type="analyzer"
              status={agentStates.Researcher.status}
              message={agentStates.Researcher.message}
            />
          </div>

          {/* Arrow to Reviewer */}
          {(stage === "review-decision" ||
            stage === "rejected" ||
            stage === "approved" ||
            stage === "synthesizer" ||
            stage === "complete") && (
            <div className="flex-shrink-0">
              <FlowArrow
                type="forward"
                animated={stage === "review-decision"}
                direction="horizontal"
              />
            </div>
          )}

          {/* Agent 2: Reviewer */}
          {(stage === "review-decision" ||
            stage === "rejected" ||
            stage === "approved" ||
            stage === "synthesizer" ||
            stage === "complete") && (
            <div className="flex-shrink-0">
              <AgentNode
                type="reviewer"
                status={agentStates.Reviewer.status}
                message={agentStates.Reviewer.message}
              />
            </div>
          )}

          {/* Approval Arrow */}
          {(stage === "approved" ||
            stage === "synthesizer" ||
            stage === "complete") && (
            <div className="flex-shrink-0">
              <FlowArrow
                type="approve"
                animated={stage === "approved"}
                direction="horizontal"
              />
            </div>
          )}

          {/* Agent 3: Synthesizer */}
          {(stage === "synthesizer" || stage === "complete") && (
            <div className="flex-shrink-0">
              <AgentNode
                type="generator"
                status={agentStates.Synthesizer.status}
                message={agentStates.Synthesizer.message}
              />
            </div>
          )}
        </div>

        {/* Rejection Feedback Loop - Curved Arrow Above */}
        {stage === "rejected" && (
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] -mt-12">
            <div className="relative animate-fade-in">
              {/* Curved SVG Arrow */}
              <svg
                viewBox="0 0 400 100"
                className="w-full h-24"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* Glow effect */}
                <defs>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                    <feMerge>
                      <feMergeNode in="coloredBlur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                  <linearGradient
                    id="errorGradient"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="0%"
                  >
                    <stop
                      offset="0%"
                      style={{ stopColor: "hsl(0 84% 60%)", stopOpacity: 1 }}
                    />
                    <stop
                      offset="100%"
                      style={{ stopColor: "hsl(0 84% 70%)", stopOpacity: 1 }}
                    />
                  </linearGradient>
                </defs>

                {/* Curved path */}
                <path
                  d="M 350 80 Q 200 10, 50 80"
                  stroke="url(#errorGradient)"
                  strokeWidth="3"
                  fill="none"
                  filter="url(#glow)"
                  strokeDasharray="1000"
                  strokeDashoffset="0"
                  className="animate-flow"
                />

                {/* Arrow head (pointing left/back) */}
                <polygon
                  points="45,75 55,80 45,85"
                  fill="hsl(0 84% 60%)"
                  filter="url(#glow)"
                  className="animate-pulse"
                />
              </svg>

              {/* Rejection Label */}
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-2">
                <div className="bg-error/20 backdrop-blur-sm border-2 border-error/50 rounded-full px-4 py-1.5 flex items-center gap-2 animate-glow-pulse">
                  <RotateCcw
                    className="w-4 h-4 text-error animate-spin"
                    style={{ animationDuration: "3s" }}
                  />
                  <span className="text-sm font-semibold text-error">
                    Quality Check Failed - Refining...
                  </span>
                </div>
              </div>

              {/* Particle effects along the curve */}
              <div className="absolute top-8 left-1/4 w-2 h-2 bg-error rounded-full animate-pulse" />
              <div
                className="absolute top-4 left-1/2 w-1.5 h-1.5 bg-error rounded-full animate-pulse"
                style={{ animationDelay: "0.3s" }}
              />
              <div
                className="absolute top-8 right-1/4 w-2 h-2 bg-error rounded-full animate-pulse"
                style={{ animationDelay: "0.6s" }}
              />
            </div>
          </div>
        )}

        {/* Completion indicator */}
        {stage === "complete" && (
          <div className="text-center mt-12 animate-scale-in">
            <div className="inline-block relative">
              {/* Celebration glow */}
              <div className="absolute inset-0 bg-success/30 blur-3xl animate-pulse" />
              <div className="relative p-6 rounded-full bg-success/10 border-2 border-success/50">
                <Check className="w-16 h-16 text-success animate-scale-in" />
              </div>
            </div>
            <p className="text-success font-bold text-xl mt-6 animate-slide-up">
              Research Complete! 🎉
            </p>
            <p className="text-muted-foreground mt-2">
              Your comprehensive report is ready
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
