import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState, useRef } from "react";
import {
  CheckCircle, Loader2, XCircle,
  Database, Accessibility, Search, LayoutDashboard, BarChart3, Target,
} from "lucide-react";

interface ProgressStep {
  step: string;
  detail: string;
  status: string;
  phase: string;
}

interface ScanProgressProps {
  scanId: string;
  status: string;
  startedAt: string;
}

const PHASE_CONFIG: Record<string, { icon: typeof Database; color: string }> = {
  "Setup": { icon: Target, color: "text-muted" },
  "Phase 1: Data Quality": { icon: Database, color: "text-orange-400" },
  "Phase 2: Accessibility": { icon: Accessibility, color: "text-red-400" },
  "Phase 3: GEO": { icon: Search, color: "text-purple-400" },
  "Phase 4: UX & Performance": { icon: LayoutDashboard, color: "text-blue-400" },
  "Phase 5: SEO": { icon: BarChart3, color: "text-green-400" },
  "Phase 6: Baseline": { icon: Target, color: "text-cyan-400" },
  "Saving": { icon: Database, color: "text-muted" },
  "Complete": { icon: CheckCircle, color: "text-green-400" },
  "Error": { icon: XCircle, color: "text-red-400" },
};

function getPhaseConfig(phase: string) {
  return PHASE_CONFIG[phase] || PHASE_CONFIG["Setup"];
}

export function ScanProgress({ scanId, status, startedAt }: ScanProgressProps) {
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (status !== "running" && status !== "pending") return;
    const start = new Date(startedAt).getTime();
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [status, startedAt]);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const eventSource = new EventSource(`${apiUrl}/api/scans/${scanId}/progress`);

    eventSource.onmessage = (event) => {
      const data: ProgressStep = JSON.parse(event.data);
      setSteps((prev) => [...prev, data]);
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [scanId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [steps]);

  if (status !== "running" && status !== "pending") return null;

  const isDone = steps.length > 0 && (steps[steps.length - 1].status === "completed" || steps[steps.length - 1].status === "failed");

  // Group steps by phase
  const phases: { phase: string; steps: ProgressStep[] }[] = [];
  let currentPhase = "";
  for (const step of steps) {
    if (step.phase !== currentPhase) {
      currentPhase = step.phase;
      phases.push({ phase: currentPhase, steps: [step] });
    } else {
      phases[phases.length - 1].steps.push(step);
    }
  }

  // Count issues per phase
  const activePhase = phases.length > 0 ? phases[phases.length - 1].phase : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          {!isDone && (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Loader2 className="w-5 h-5 text-brand" />
            </motion.div>
          )}
          {isDone && steps[steps.length - 1].status === "completed" && (
            <CheckCircle className="w-5 h-5 text-green-400" />
          )}
          {isDone && steps[steps.length - 1].status === "failed" && (
            <XCircle className="w-5 h-5 text-red-400" />
          )}
          <div>
            <h3 className="text-sm font-bold text-ink">
              {isDone ? "Full Site Audit Complete" : "Running 6-Phase Site Audit..."}
            </h3>
            {activePhase && !isDone && (
              <p className="text-xs text-muted mt-0.5">{activePhase}</p>
            )}
          </div>
        </div>
        <span className="text-xs text-muted font-mono tabular-nums">
          {Math.floor(elapsed / 60)}:{(elapsed % 60).toString().padStart(2, "0")}
        </span>
      </div>

      {/* Phase badges */}
      <div className="flex gap-1.5 px-5 py-3 border-b border-white/[0.06] overflow-x-auto">
        {["Phase 1: Data Quality", "Phase 2: Accessibility", "Phase 3: GEO", "Phase 4: UX & Performance", "Phase 5: SEO", "Phase 6: Baseline"].map((p) => {
          const config = getPhaseConfig(p);
          const phaseSteps = phases.find(pp => pp.phase === p);
          const isActive = activePhase === p;
          const isCompleted = phaseSteps && phases.findIndex(pp => pp.phase === p) < phases.length - 1;
          const Icon = config.icon;

          return (
            <div
              key={p}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border whitespace-nowrap transition-all ${
                isActive
                  ? "border-brand/40 bg-brand/10 text-brand"
                  : isCompleted
                    ? "border-white/10 bg-white/[0.04] text-muted"
                    : "border-white/[0.04] bg-transparent text-muted/40"
              }`}
            >
              {isCompleted ? (
                <CheckCircle className="w-3 h-3 text-green-400" />
              ) : isActive ? (
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
                  <Loader2 className="w-3 h-3" />
                </motion.div>
              ) : (
                <Icon className="w-3 h-3" />
              )}
              {p.replace("Phase ", "P").split(":")[0]}
            </div>
          );
        })}
      </div>

      {/* Steps log */}
      <div ref={scrollRef} className="max-h-80 overflow-y-auto scrollbar-thin">
        <div className="px-5 py-3">
          <AnimatePresence>
            {phases.map((phaseGroup, pi) => {
              const config = getPhaseConfig(phaseGroup.phase);
              const PhaseIcon = config.icon;
              const isPhaseHeader = phaseGroup.phase.startsWith("Phase");

              return (
                <div key={pi}>
                  {isPhaseHeader && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex items-center gap-2 mt-3 mb-2 first:mt-0"
                    >
                      <PhaseIcon className={`w-4 h-4 ${config.color}`} />
                      <span className={`text-xs font-bold uppercase tracking-wider ${config.color}`}>
                        {phaseGroup.phase}
                      </span>
                      <div className="flex-1 h-px bg-white/[0.06]" />
                    </motion.div>
                  )}
                  {phaseGroup.steps.map((step, si) => {
                    const isLast = pi === phases.length - 1 && si === phaseGroup.steps.length - 1;
                    const isComplete = step.status === "completed";
                    const isFailed = step.status === "failed";
                    const isFound = step.step.startsWith("Found:");

                    return (
                      <motion.div
                        key={`${pi}-${si}`}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.15 }}
                        className={`flex items-start gap-2.5 py-1.5 ${isFound ? "ml-4" : ""}`}
                      >
                        <div className="mt-0.5 flex-shrink-0">
                          {isComplete ? (
                            <CheckCircle className="w-3.5 h-3.5 text-green-400" />
                          ) : isFailed ? (
                            <XCircle className="w-3.5 h-3.5 text-red-400" />
                          ) : isLast && !isDone ? (
                            <div className="w-3.5 h-3.5 rounded-full border-2 border-brand border-t-transparent animate-spin" />
                          ) : isFound ? (
                            <div className="w-1.5 h-1.5 rounded-full bg-muted/50 mt-1 ml-1" />
                          ) : (
                            <CheckCircle className="w-3.5 h-3.5 text-brand/40" />
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className={`text-xs leading-relaxed ${
                            isLast && !isDone ? "text-ink font-medium" :
                            isFound ? "text-muted/70" : "text-muted"
                          }`}>
                            {isFound ? step.step.replace("Found: ", "") : step.step}
                          </p>
                          {step.detail && !isFound && (
                            <p className="text-[11px] text-muted/50 truncate mt-0.5">
                              {step.detail}
                            </p>
                          )}
                          {step.detail && isFound && (
                            <p className="text-[11px] text-muted/40 truncate">
                              {step.detail}
                            </p>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              );
            })}
          </AnimatePresence>

          {steps.length === 0 && (
            <div className="flex items-center gap-2 py-4 text-sm text-muted">
              <Loader2 className="w-4 h-4 animate-spin" />
              Connecting to scan progress...
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
