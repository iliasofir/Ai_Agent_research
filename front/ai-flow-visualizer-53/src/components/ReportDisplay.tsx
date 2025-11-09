import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download, FileText, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface ReportDisplayProps {
  report: string;
  onNewResearch: () => void;
}

export const ReportDisplay = ({
  report,
  onNewResearch,
}: ReportDisplayProps) => {
  const [isExporting, setIsExporting] = useState(false);

  // Log pour déboguer
  console.log(
    "📄 ReportDisplay rendu avec rapport de longueur:",
    report?.length || 0
  );

  const handleExport = async () => {
    setIsExporting(true);

    // Simulate export delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Create a blob with the markdown content
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `research-report-${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setIsExporting(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-primary/10">
            <FileText className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-foreground">
              Research Report
            </h2>
            <p className="text-sm text-muted-foreground">
              Generated on {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            onClick={handleExport}
            disabled={isExporting}
            className="bg-primary hover:opacity-90 transition-opacity"
          >
            <Download className="w-4 h-4 mr-2" />
            {isExporting ? "Exporting..." : "Download"}
          </Button>
          <Button
            onClick={onNewResearch}
            variant="outline"
            className="border-primary/50 hover:bg-primary/10"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            New Research
          </Button>
        </div>
      </div>

      {/* Report Content */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent blur-3xl" />
        <div className="relative bg-card/80 backdrop-blur-xl border border-border/50 rounded-2xl p-8 shadow-card">
          {!report || report.trim() === "" ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg">
                Aucun rapport disponible. Le rapport est en cours de
                génération...
              </p>
            </div>
          ) : (
            <div className="prose prose-invert prose-lg max-w-none">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-3xl font-bold text-foreground mb-4 pb-2 border-b border-border">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-2xl font-semibold text-foreground mt-8 mb-4">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-xl font-semibold text-foreground mt-6 mb-3">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="text-foreground/90 leading-relaxed mb-4">
                      {children}
                    </p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside space-y-2 text-foreground/90 mb-4">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside space-y-2 text-foreground/90 mb-4">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => <li className="ml-4">{children}</li>,
                  strong: ({ children }) => (
                    <strong className="font-semibold text-primary">
                      {children}
                    </strong>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-foreground">{children}</em>
                  ),
                  hr: () => <hr className="border-border my-6" />,
                }}
              >
                {report}
              </ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
