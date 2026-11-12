import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Loader2 } from "lucide-react";
import type { AIAnalysis } from "../../types";

interface AIAnalysisPanelProps {
  analysis: AIAnalysis | undefined;
  isLoading: boolean;
}

function useTypewriter(text: string, speed = 15) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    if (!text) return;
    setDisplayed("");
    let i = 0;
    const timer = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(timer);
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed]);
  return displayed;
}

export function AIAnalysisPanel({ analysis, isLoading }: AIAnalysisPanelProps) {
  const explanation = useTypewriter(analysis?.explanation || "");

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3 }}
      className="overflow-hidden"
    >
      <div className="rounded-xl bg-gradient-to-br from-brand/[0.08] to-purple-500/[0.04] border border-brand/20 p-5">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-7 h-7 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-brand" />
          </div>
          <h4 className="text-sm font-bold text-ink">AI Analysis</h4>
          {analysis?.model_name && (
            <span className="text-xs text-muted">· {analysis.model_name}</span>
          )}
        </div>

        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-muted py-4">
            <Loader2 className="w-4 h-4 animate-spin" />
            Analyzing violation...
          </div>
        )}

        {analysis && (
          <div className="space-y-4">
            <div>
              <h5 className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">
                Explanation
              </h5>
              <p className="text-sm text-ink leading-relaxed">{explanation}</p>
            </div>

            {analysis.suggested_fix && (
              <div>
                <h5 className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">
                  Suggested Fix
                </h5>
                <pre className="text-xs bg-black/40 text-green-400 rounded-lg p-4 overflow-x-auto border border-white/[0.06]">
                  <code>{analysis.suggested_fix}</code>
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
