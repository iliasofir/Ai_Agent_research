import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Upload, Search, FileText } from "lucide-react";

interface InputFormProps {
  onSubmit: (topic: string, files: File[], searchOnline: boolean) => void;
}

export const InputForm = ({ onSubmit }: InputFormProps) => {
  const [topic, setTopic] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [searchOnline, setSearchOnline] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "application/pdf"
    );
    setFiles((prev) => [...prev, ...droppedFiles]);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const handleSubmit = () => {
    if (topic.trim()) {
      onSubmit(topic, files, searchOnline);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6 animate-slide-up">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20 blur-3xl rounded-full" />
        <div className="relative bg-card/80 backdrop-blur-xl border border-border/50 rounded-2xl p-8 shadow-card">
          <div className="space-y-6">
            {/* Topic Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground flex items-center gap-2">
                <Search className="w-4 h-4 text-primary" />
                Research Topic
              </label>
              <Input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter your research topic..."
                className="bg-background/50 border-border/50 focus:border-primary transition-colors text-lg h-12"
              />
            </div>

            {/* File Upload Zone */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary" />
                Research Papers (Optional)
              </label>
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-8 transition-all ${
                  isDragging
                    ? "border-primary bg-primary/10 scale-105"
                    : "border-border/50 bg-background/30"
                }`}
              >
                <input
                  type="file"
                  accept=".pdf"
                  multiple
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-input"
                />
                <label
                  htmlFor="file-input"
                  className="flex flex-col items-center gap-3 cursor-pointer"
                >
                  <div className="p-4 rounded-full bg-primary/10">
                    <Upload className="w-8 h-8 text-primary" />
                  </div>
                  <div className="text-center">
                    <p className="text-foreground font-medium">
                      Drop PDF files here or click to browse
                    </p>
                    <p className="text-muted-foreground text-sm mt-1">
                      Upload research papers for analysis
                    </p>
                  </div>
                </label>
              </div>

              {/* Uploaded Files */}
              {files.length > 0 && (
                <div className="space-y-2 mt-4">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-muted/50 rounded-lg p-3 animate-scale-in"
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-primary" />
                        <span className="text-sm text-foreground truncate">
                          {file.name}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="text-error hover:text-error hover:bg-error/10"
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Search Online Checkbox */}
            {files.length === 0 && (
              <div className="flex items-center space-x-2 pt-2">
                <Checkbox
                  id="search-online"
                  checked={searchOnline}
                  onCheckedChange={(checked) =>
                    setSearchOnline(checked as boolean)
                  }
                />
                <label
                  htmlFor="search-online"
                  className="text-sm font-medium text-foreground cursor-pointer"
                >
                  Automatically search and analyze papers online
                </label>
              </div>
            )}

            {/* Submit Button */}
            <Button
              onClick={handleSubmit}
              disabled={!topic.trim()}
              className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity shadow-glow"
            >
              Start Research
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
