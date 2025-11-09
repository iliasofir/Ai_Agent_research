import { Brain, Search, FileText, Sparkles } from "lucide-react";

interface AgentNodeProps {
  type: "analyzer" | "reviewer" | "generator";
  status: "idle" | "thinking" | "approved" | "rejected";
  message: string;
}

export const AgentNode = ({ type, status, message }: AgentNodeProps) => {
  const icons = {
    analyzer: Brain,
    reviewer: Search,
    generator: FileText,
  };

  const Icon = icons[type];

  const getStatusColor = () => {
    if (status === "approved") return "success";
    if (status === "rejected") return "error";
    return "primary";
  };

  const statusColor = getStatusColor();

  const getTitleColor = () => {
    if (status === "approved") return "text-success";
    if (status === "rejected") return "text-error";
    if (status === "thinking") return "text-primary";
    return "text-foreground";
  };

  return (
    <div className="flex flex-col items-center gap-4 animate-scale-in">
      <div className="relative">
        {/* Outer glow rings */}
        {status === "thinking" && (
          <>
            <div className={`absolute inset-0 w-32 h-32 -translate-x-4 -translate-y-4 rounded-full bg-${statusColor}/10 blur-2xl animate-pulse`} />
            <div className={`absolute inset-0 w-28 h-28 -translate-x-2 -translate-y-2 rounded-full bg-${statusColor}/20 blur-xl animate-glow-pulse`} />
          </>
        )}

        {/* Main agent card */}
        <div
          className={`relative w-28 h-28 rounded-2xl bg-gradient-to-br from-${statusColor} to-${statusColor}/70 
          flex items-center justify-center shadow-glow-strong border-2 border-${statusColor}/30
          ${status === "thinking" ? "animate-float" : ""}
          ${status === "approved" ? "scale-105" : ""}
          ${status === "rejected" ? "animate-pulse" : ""}
          transition-all duration-500`}
        >
          {/* Background shimmer effect */}
          {status === "thinking" && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer rounded-2xl" 
                 style={{ backgroundSize: '200% 100%' }} />
          )}

          {/* Icon */}
          <div className="relative z-10">
            <Icon className={`w-14 h-14 text-background ${status === "thinking" ? "animate-pulse" : ""}`} />
          </div>

          {/* Thinking Indicator - Enhanced */}
          {status === "thinking" && (
            <div className="absolute -bottom-3 -right-3">
              <div className="relative">
                <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center shadow-lg animate-bounce">
                  <Sparkles className="w-5 h-5 text-primary animate-spin" style={{ animationDuration: '3s' }} />
                </div>
                {/* Pulsing ring */}
                <div className="absolute inset-0 rounded-full bg-primary/30 animate-ping" />
              </div>
            </div>
          )}

          {/* Approved check mark */}
          {status === "approved" && (
            <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-success border-2 border-background flex items-center justify-center animate-scale-in">
              <svg className="w-5 h-5 text-background" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}

          {/* Rejected X mark */}
          {status === "rejected" && (
            <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-error border-2 border-background flex items-center justify-center animate-scale-in">
              <svg className="w-5 h-5 text-background" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}
        </div>

        {/* Particle effects for thinking state */}
        {status === "thinking" && (
          <>
            <div className={`absolute top-0 left-0 w-2 h-2 bg-${statusColor} rounded-full animate-ping`} />
            <div className={`absolute top-0 right-0 w-1.5 h-1.5 bg-${statusColor} rounded-full animate-ping`} style={{ animationDelay: '0.5s' }} />
            <div className={`absolute bottom-0 left-0 w-1.5 h-1.5 bg-${statusColor} rounded-full animate-ping`} style={{ animationDelay: '1s' }} />
            <div className={`absolute bottom-0 right-0 w-2 h-2 bg-${statusColor} rounded-full animate-ping`} style={{ animationDelay: '1.5s' }} />
          </>
        )}
      </div>

      {/* Message */}
      <div className="text-center space-y-1 max-w-[200px]">
        <h3 className={`text-base font-bold ${getTitleColor()} transition-colors duration-300`}>
          {type === "analyzer" && "Research Analyzer"}
          {type === "reviewer" && "Quality Reviewer"}
          {type === "generator" && "Report Generator"}
        </h3>
        <p className={`text-xs font-mono px-3 py-1 rounded-full ${
          status === "thinking" ? `bg-${statusColor}/10 text-${statusColor}` : 'text-muted-foreground'
        } transition-all duration-300`}>
          {message}
        </p>
      </div>
    </div>
  );
};
