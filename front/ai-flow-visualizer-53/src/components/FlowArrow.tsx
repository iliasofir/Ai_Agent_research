import { ArrowRight, Check, MoveRight, Zap } from "lucide-react";

interface FlowArrowProps {
  type: "forward" | "reject" | "approve";
  animated?: boolean;
  direction?: "horizontal" | "vertical";
}

export const FlowArrow = ({ type, animated = false, direction = "vertical" }: FlowArrowProps) => {
  const getArrowColor = () => {
    if (type === "approve") return "success";
    if (type === "reject") return "error";
    return "primary";
  };

  const color = getArrowColor();

  const getIcon = () => {
    if (type === "approve") return Check;
    return MoveRight;
  };

  const Icon = getIcon();

  if (direction === "horizontal") {
    return (
      <div className="flex items-center justify-center">
        <div className="relative">
          {/* Animated glow */}
          {animated && (
            <>
              <div className={`absolute inset-0 bg-${color}/30 blur-2xl animate-pulse`} />
              <div className={`absolute -inset-4 bg-${color}/20 blur-3xl animate-glow-pulse`} />
            </>
          )}

          {/* Horizontal Arrow with flowing particles */}
          <div className="relative">
            {/* Arrow line */}
            <div className={`w-20 h-1 bg-gradient-to-r from-${color}/50 to-${color} rounded-full relative overflow-hidden`}>
              {animated && (
                <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-${color} to-transparent animate-shimmer`} 
                     style={{ backgroundSize: '200% 100%' }} />
              )}
            </div>

            {/* Arrow head */}
            <div className={`absolute -right-2 top-1/2 -translate-y-1/2 ${animated ? 'animate-pulse' : ''}`}>
              <Icon className={`w-5 h-5 text-${color}`} />
            </div>

            {/* Floating particles */}
            {animated && (
              <>
                <div className={`absolute top-1/2 left-0 w-1.5 h-1.5 bg-${color} rounded-full animate-flow`} 
                     style={{ animation: 'flow-particle 1.5s ease-in-out infinite' }} />
                <div className={`absolute top-1/2 left-1/4 w-1 h-1 bg-${color}/70 rounded-full animate-flow`} 
                     style={{ animation: 'flow-particle 1.5s ease-in-out infinite 0.3s' }} />
                <div className={`absolute top-1/2 left-1/2 w-1.5 h-1.5 bg-${color} rounded-full animate-flow`} 
                     style={{ animation: 'flow-particle 1.5s ease-in-out infinite 0.6s' }} />
              </>
            )}

            {/* Status label */}
            <div className={`absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-${color}/10 backdrop-blur-sm border border-${color}/30 rounded-full px-3 py-1`}>
              <span className={`text-xs font-medium text-${color}`}>
                {type === "approve" && "Validated ✓"}
                {type === "forward" && "Analyzing..."}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Vertical version (kept for compatibility)
  return (
    <div className="flex items-center justify-center my-8">
      <div className="relative">
        {animated && (
          <>
            <div className={`absolute inset-0 bg-${color}/20 blur-xl animate-pulse`} />
            <div className={`absolute -inset-2 bg-${color}/10 blur-2xl animate-glow-pulse`} />
          </>
        )}

        <div className={`relative flex items-center gap-2 px-6 py-3 rounded-full bg-${color}/10 border-2 border-${color}/50 ${animated ? "animate-float" : ""}`}>
          <Icon className={`w-6 h-6 text-${color}`} />
          <span className={`text-sm font-medium text-${color}`}>
            {type === "approve" && "Validated ✓"}
            {type === "forward" && "Processing..."}
          </span>
        </div>
      </div>
    </div>
  );
};
