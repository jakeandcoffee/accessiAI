import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Sparkles, Code } from "lucide-react";
import { clsx } from "clsx";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import { AIAnalysisPanel } from "./AIAnalysisPanel";
import { useAIAnalysis, useUpdateViolationStatus } from "../../hooks/useScans";
import type { Violation } from "../../types";

interface ViolationCardProps {
  violation: Violation;
  index: number;
}

export function ViolationCard({ violation, index }: ViolationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAI, setShowAI] = useState(false);
  const aiAnalysis = useAIAnalysis();
  const updateStatus = useUpdateViolationStatus();

  const latestAnalysis = violation.ai_analyses?.[violation.ai_analyses.length - 1];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, type: "spring", stiffness: 300, damping: 25 }}
      className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg overflow-hidden"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-white/[0.03] transition-colors"
        aria-expanded={isExpanded}
      >
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-4 h-4 text-muted" />
        </motion.div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <code className="text-xs bg-white/[0.06] border border-white/[0.06] px-1.5 py-0.5 rounded font-mono text-ink">
              {violation.rule_id}
            </code>
            <Badge variant={violation.impact}>{violation.impact}</Badge>
            <Badge variant={violation.status}>{violation.status.replace("_", " ")}</Badge>
          </div>
          <p className="text-sm text-ink mt-1 truncate">{violation.description}</p>
        </div>
        {violation.wcag_criteria && (
          <span className="text-xs text-muted whitespace-nowrap">WCAG {violation.wcag_criteria}</span>
        )}
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-white/[0.06] pt-4 space-y-4">
              {violation.affected_elements?.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-muted uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Code className="w-3.5 h-3.5" /> Affected Elements
                  </h4>
                  <div className="space-y-2">
                    {violation.affected_elements.map((el) => (
                      <div key={el.id} className="rounded-lg bg-white/[0.03] border border-white/[0.06] p-3">
                        <code className="text-xs text-muted block mb-1">{el.selector}</code>
                        <pre className="text-xs bg-black/40 text-green-400 rounded-lg p-3 overflow-x-auto border border-white/[0.06]">
                          <code>{el.html}</code>
                        </pre>
                        {el.failure_summary && (
                          <p className="text-xs text-muted mt-2">{el.failure_summary}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2 flex-wrap">
                <select
                  value={violation.status}
                  onChange={(e) =>
                    updateStatus.mutate({ id: violation.id, status: e.target.value })
                  }
                  className="rounded-lg border border-white/10 bg-white/[0.04] text-ink px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-brand/50"
                  aria-label="Change violation status"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="ignored">Ignored</option>
                </select>

                <Button
                  size="sm"
                  variant={showAI ? "secondary" : "primary"}
                  onClick={() => {
                    if (!latestAnalysis && !showAI) {
                      aiAnalysis.mutate(violation.id);
                    }
                    setShowAI(!showAI);
                  }}
                  isLoading={aiAnalysis.isPending}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  {showAI ? "Hide AI" : "AI Analysis"}
                </Button>

                {violation.help_url && (
                  <a
                    href={violation.help_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={clsx(
                      "inline-flex items-center gap-1 rounded-lg border border-white/10 px-3 py-1.5 text-xs",
                      "text-muted hover:text-ink hover:bg-white/5 transition-colors",
                    )}
                  >
                    Learn more
                  </a>
                )}
              </div>

              <AnimatePresence>
                {showAI && (
                  <AIAnalysisPanel
                    analysis={latestAnalysis || (aiAnalysis.data as typeof latestAnalysis)}
                    isLoading={aiAnalysis.isPending}
                  />
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
