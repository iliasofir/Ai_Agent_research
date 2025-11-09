import { useState } from "react";
import { InputForm } from "@/components/InputForm";
import { WorkflowAnimation } from "@/components/WorkflowAnimation";
import { ReportDisplay } from "@/components/ReportDisplay";
import { Sparkles } from "lucide-react";
import {
  sendResearchRequest,
  sendResearchWithPDFs,
  uploadPDF,
  ResearchStatus,
} from "@/services/researchService";
import { useToast } from "@/hooks/use-toast";

type AppState = "input" | "processing" | "results";

const Index = () => {
  const [appState, setAppState] = useState<AppState>("input");
  const [report, setReport] = useState("");
  const [currentTopic, setCurrentTopic] = useState("");
  const [researchId, setResearchId] = useState<string | null>(null);
  const { toast } = useToast();

  const handleStartResearch = async (
    topic: string,
    files: File[],
    searchOnline: boolean
  ) => {
    console.log("Starting research:", { topic, files, searchOnline });
    setCurrentTopic(topic);
    setAppState("processing");

    try {
      let response;

      // Si des PDFs sont fournis, les uploader d'abord
      if (files.length > 0) {
        toast({
          title: "Upload des PDFs",
          description: `Upload de ${files.length} fichier(s) en cours...`,
        });

        const fileIds: string[] = [];

        // Upload chaque PDF
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          try {
            const uploadResult = await uploadPDF(file, topic);
            fileIds.push(uploadResult.file_id);

            toast({
              title: "PDF uploadé",
              description: `${uploadResult.filename} (${uploadResult.page_count} pages)`,
            });
          } catch (error) {
            console.error(`Erreur lors de l'upload de ${file.name}:`, error);
            toast({
              variant: "destructive",
              title: "Erreur d'upload",
              description: `Impossible d'uploader ${file.name}`,
            });
          }
        }

        if (fileIds.length === 0) {
          throw new Error("Aucun PDF n'a pu être uploadé");
        }

        // Lancer la recherche avec les PDFs
        toast({
          title: "Recherche lancée",
          description: `Analyse de ${fileIds.length} PDF(s)...`,
        });

        response = await sendResearchWithPDFs(topic, fileIds);
      } else {
        // Recherche sans PDFs (ArXiv/Web)
        response = await sendResearchRequest(topic);
      }

      toast({
        title: "Connexion établie",
        description: "Flux en temps réel activé",
      });

      // Note: Le workflow sera géré par le WebSocket
      // La completion sera déclenchée par le message workflow_status: completed
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Erreur de connexion",
        description:
          "Impossible de se connecter à l'API. Vérifiez que le serveur est démarré.",
      });
      console.error("Erreur lors de la recherche:", error);
      // Retour à l'écran d'entrée en cas d'erreur
      setAppState("input");
    }
  };

  const handleWorkflowComplete = (generatedReport: string) => {
    setReport(generatedReport);
    setTimeout(() => setAppState("results"), 500);
  };

  const handleNewResearch = () => {
    setAppState("input");
    setReport("");
    setCurrentTopic("");
    setResearchId(null);
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-primary/10 rounded-full blur-3xl" />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="pt-12 pb-8 text-center">
          <div className="inline-flex items-center gap-3 mb-4 animate-scale-in">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-primary to-secondary shadow-glow">
              <Sparkles className="w-8 h-8 text-background" />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-4 animate-slide-up">
            AI Research Assistant
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto px-4 animate-fade-in">
            Transform research papers into comprehensive insights with our
            intelligent multi-agent analysis system
          </p>
        </header>

        {/* Main Content Area */}
        <main className="container mx-auto px-4 pb-16">
          {appState === "input" && <InputForm onSubmit={handleStartResearch} />}

          {appState === "processing" && (
            <WorkflowAnimation
              onComplete={handleWorkflowComplete}
              topic={currentTopic}
              researchId={researchId}
            />
          )}

          {appState === "results" && (
            <ReportDisplay report={report} onNewResearch={handleNewResearch} />
          )}
        </main>

        {/* Footer */}
        <footer className="text-center pb-8 text-muted-foreground text-sm">
          <p>Powered by advanced AI agents • Real-time quality validation</p>
        </footer>
      </div>
    </div>
  );
};

export default Index;
