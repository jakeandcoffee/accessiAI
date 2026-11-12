import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  Globe,
  Lock,
  KeyRound,
  Code,
  Eye,
  BarChart3,
  Loader2,
  CheckCircle,
  XCircle,
  Download,
  ChevronDown,
  Search,
  AlertTriangle,
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { clsx } from "clsx";
import { Card } from "../common/Card";
import { Button } from "../common/Button";
import api from "../../services/api";
import {
  getSecurityResults,
  downloadSecurityReport,
  type SecurityScanResults,
  type SecurityFinding,
} from "../../services/securityService";

// ── Constants ──

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ff5c5c",
  high: "#ff9f43",
  medium: "#ffd43b",
  low: "#5c9cff",
  info: "#7a8ba8",
};

const SEVERITY_BADGE: Record<string, string> = {
  critical: "critical",
  high: "serious",
  medium: "moderate",
  low: "minor",
  info: "open",
};

interface ProgressStep {
  step: string;
  detail: string;
  status: string;
  phase: string;
}

const PHASE_LABELS = [
  "Phase 1: HTTP Headers",
  "Phase 2: SSL/TLS",
  "Phase 3: Cookies",
  "Phase 4: Content Security",
  "Phase 5: Info Disclosure",
  "Scoring",
];

const PHASE_CONFIG: Record<string, { icon: typeof Globe; color: string }> = {
  Setup: { icon: Search, color: "text-muted" },
  "Phase 1: HTTP Headers": { icon: Globe, color: "text-blue-400" },
  "Phase 2: SSL/TLS": { icon: Lock, color: "text-green-400" },
  "Phase 3: Cookies": { icon: KeyRound, color: "text-orange-400" },
  "Phase 4: Content Security": { icon: Code, color: "text-purple-400" },
  "Phase 5: Info Disclosure": { icon: Eye, color: "text-red-400" },
  Scoring: { icon: BarChart3, color: "text-cyan-400" },
  Complete: { icon: CheckCircle, color: "text-green-400" },
  Error: { icon: XCircle, color: "text-red-400" },
};

function getPhaseConfig(phase: string) {
  return PHASE_CONFIG[phase] || PHASE_CONFIG["Setup"];
}

// ── Hooks ──

function useCountUp(target: number, duration = 1200) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (target === 0) {
      setCount(0);
      return;
    }
    const start = performance.now();
    function tick(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [target, duration]);
  return count;
}

// ── Sub-components ──

function SecurityScoreGauge({ score, size = 180 }: { score: number; size?: number }) {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  function getColor(s: number) {
    if (s >= 80) return "#4ade80";
    if (s >= 60) return "#ffd43b";
    if (s >= 40) return "#ff9f43";
    return "#ff5c5c";
  }
  const color = getColor(score);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={strokeWidth} />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius} fill="none"
          stroke={color} strokeWidth={strokeWidth} strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ width: size, height: size }}>
        <motion.span className="text-4xl font-bold tabular-nums" style={{ color }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
          {score}
        </motion.span>
        <span className="text-xs text-muted font-medium mt-1">out of 100</span>
      </div>
    </div>
  );
}

function SeverityPie({ findings }: { findings: SecurityFinding[] }) {
  const counts: Record<string, number> = {};
  for (const f of findings) counts[f.severity] = (counts[f.severity] || 0) + 1;
  const chartData = Object.entries(counts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    color: SEVERITY_COLORS[name] || "#7a8ba8",
  }));

  if (chartData.length === 0) return <p className="text-center text-muted text-sm py-12">No findings</p>;

  return (
    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value" animationBegin={300} animationDuration={1200}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} stroke="none" />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: "rgba(18, 18, 30, 0.9)", border: "1px solid rgba(255, 255, 255, 0.1)", borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.3)", color: "#e2e8f0" }} />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex justify-center gap-4 mt-2">
        {chartData.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs text-muted">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
            {d.name} ({d.value})
          </div>
        ))}
      </div>
    </motion.div>
  );
}

function SecurityStatCard({ label, value, icon: Icon, color, delay = 0 }: { label: string; value: number; icon: typeof Shield; color: string; delay?: number }) {
  const displayValue = useCountUp(value);
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: "spring", stiffness: 300, damping: 24 }}
      whileHover={{ y: -2, boxShadow: "0 12px 40px rgba(108,142,255,0.06)" }}
      className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg p-5"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-muted">{label}</span>
        <div className={clsx("w-9 h-9 rounded-lg flex items-center justify-center border border-white/[0.06]", color)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="text-3xl font-bold tabular-nums text-ink">{displayValue}</div>
    </motion.div>
  );
}

function FindingCard({ finding, index }: { finding: SecurityFinding; index: number }) {
  const [open, setOpen] = useState(false);
  const badgeVariant = SEVERITY_BADGE[finding.severity] || "open";
  const severityColor = SEVERITY_COLORS[finding.severity] || "#7a8ba8";

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }} className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-white/[0.02] transition-colors">
        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: severityColor }} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-ink truncate">{finding.title}</p>
          <p className="text-xs text-muted truncate mt-0.5">{finding.description}</p>
        </div>
        <span className={clsx(
          "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold flex-shrink-0",
          badgeVariant === "critical" && "bg-red-500/15 text-red-400 border-red-500/20",
          badgeVariant === "serious" && "bg-orange-500/15 text-orange-400 border-orange-500/20",
          badgeVariant === "moderate" && "bg-yellow-500/15 text-yellow-400 border-yellow-500/20",
          badgeVariant === "minor" && "bg-blue-500/15 text-blue-400 border-blue-500/20",
          badgeVariant === "open" && "bg-white/5 text-gray-400 border-white/10",
        )}>
          {finding.severity.toUpperCase()}
        </span>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown className="w-4 h-4 text-muted flex-shrink-0" />
        </motion.div>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }} className="overflow-hidden">
            <div className="px-5 pb-4 space-y-3 border-t border-white/[0.06] pt-3">
              {finding.details && (
                <div>
                  <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-1">Details</p>
                  <p className="text-sm text-ink/80">{finding.details}</p>
                </div>
              )}
              <div>
                <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-1">Recommendation</p>
                <p className="text-sm text-brand-light">{finding.recommendation}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function SecurityScanProgressView({ scanId, onComplete }: { scanId: string; onComplete: () => void }) {
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const startRef = useRef(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startRef.current) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const eventSource = new EventSource(`${apiUrl}/api/security-scan/${scanId}/progress`);

    eventSource.onmessage = (event) => {
      const data: ProgressStep = JSON.parse(event.data);
      setSteps((prev) => [...prev, data]);
      if (data.status === "completed" || data.status === "failed") {
        eventSource.close();
        setTimeout(onComplete, 600);
      }
    };

    eventSource.onerror = () => eventSource.close();
    return () => eventSource.close();
  }, [scanId, onComplete]);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [steps]);

  const isDone = steps.length > 0 && (steps[steps.length - 1].status === "completed" || steps[steps.length - 1].status === "failed");

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

  const activePhase = phases.length > 0 ? phases[phases.length - 1].phase : "";

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          {!isDone && (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
              <Loader2 className="w-5 h-5 text-brand" />
            </motion.div>
          )}
          {isDone && steps[steps.length - 1].status === "completed" && <ShieldCheck className="w-5 h-5 text-green-400" />}
          {isDone && steps[steps.length - 1].status === "failed" && <ShieldAlert className="w-5 h-5 text-red-400" />}
          <div>
            <h3 className="text-sm font-bold text-ink">{isDone ? "Security Scan Complete" : "Running Security Scan..."}</h3>
            {activePhase && !isDone && <p className="text-xs text-muted mt-0.5">{activePhase}</p>}
          </div>
        </div>
        <span className="text-xs text-muted font-mono tabular-nums">
          {Math.floor(elapsed / 60)}:{(elapsed % 60).toString().padStart(2, "0")}
        </span>
      </div>

      <div className="flex gap-1.5 px-5 py-3 border-b border-white/[0.06] overflow-x-auto">
        {PHASE_LABELS.map((p) => {
          const config = getPhaseConfig(p);
          const phaseSteps = phases.find((pp) => pp.phase === p);
          const isActive = activePhase === p;
          const isCompleted = phaseSteps && phases.findIndex((pp) => pp.phase === p) < phases.length - 1;
          const Icon = config.icon;
          return (
            <div key={p} className={clsx(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border whitespace-nowrap transition-all",
              isActive ? "border-brand/40 bg-brand/10 text-brand" : isCompleted ? "border-white/10 bg-white/[0.04] text-muted" : "border-white/[0.04] bg-transparent text-muted/40",
            )}>
              {isCompleted ? <CheckCircle className="w-3 h-3 text-green-400" /> : isActive ? (
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}><Loader2 className="w-3 h-3" /></motion.div>
              ) : <Icon className="w-3 h-3" />}
              {p.replace(/^Phase \d+: /, "")}
            </div>
          );
        })}
      </div>

      <div ref={scrollRef} className="max-h-80 overflow-y-auto scrollbar-thin">
        <div className="px-5 py-3">
          <AnimatePresence>
            {phases.map((phaseGroup, pi) => {
              const config = getPhaseConfig(phaseGroup.phase);
              const PhaseIcon = config.icon;
              const isPhaseHeader = PHASE_LABELS.includes(phaseGroup.phase);
              return (
                <div key={pi}>
                  {isPhaseHeader && (
                    <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-2 mt-3 mb-2 first:mt-0">
                      <PhaseIcon className={clsx("w-4 h-4", config.color)} />
                      <span className={clsx("text-xs font-bold uppercase tracking-wider", config.color)}>{phaseGroup.phase}</span>
                      <div className="flex-1 h-px bg-white/[0.06]" />
                    </motion.div>
                  )}
                  {phaseGroup.steps.map((step, si) => {
                    const isLast = pi === phases.length - 1 && si === phaseGroup.steps.length - 1;
                    const isComplete = step.status === "completed";
                    const isFailed = step.status === "failed";
                    const isFound = step.step.startsWith("Found:");
                    return (
                      <motion.div key={`${pi}-${si}`} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.15 }} className={clsx("flex items-start gap-2.5 py-1.5", isFound && "ml-4")}>
                        <div className="mt-0.5 flex-shrink-0">
                          {isComplete ? <CheckCircle className="w-3.5 h-3.5 text-green-400" /> : isFailed ? <XCircle className="w-3.5 h-3.5 text-red-400" /> : isLast && !isDone ? <div className="w-3.5 h-3.5 rounded-full border-2 border-brand border-t-transparent animate-spin" /> : isFound ? <div className="w-1.5 h-1.5 rounded-full bg-muted/50 mt-1 ml-1" /> : <CheckCircle className="w-3.5 h-3.5 text-brand/40" />}
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className={clsx("text-xs leading-relaxed", isLast && !isDone ? "text-ink font-medium" : isFound ? "text-muted/70" : "text-muted")}>
                            {isFound ? step.step.replace("Found: ", "") : step.step}
                          </p>
                          {step.detail && <p className={clsx("text-[11px] truncate mt-0.5", isFound ? "text-muted/40" : "text-muted/50")}>{step.detail}</p>}
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
              Connecting to security scan...
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ── Main SecuritySection ──

type SectionState = "loading" | "scanning" | "done" | "not_available";

export function SecuritySection({ scanId }: { scanId: string }) {
  const [state, setState] = useState<SectionState>("loading");
  const [securityScanId, setSecurityScanId] = useState<string | null>(null);
  const [results, setResults] = useState<SecurityScanResults | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const { data } = await api.get(`/api/scans/${scanId}/security`);
        if (cancelled) return;
        setSecurityScanId(data.security_scan_id);
        if (data.status === "completed") {
          const res = await getSecurityResults(data.security_scan_id);
          if (cancelled) return;
          setResults(res);
          setState("done");
        } else {
          setState("scanning");
        }
      } catch {
        if (cancelled) return;
        timer = setTimeout(poll, 2000);
      }
    }

    poll();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [scanId]);

  const handleScanComplete = useCallback(async () => {
    if (!securityScanId) return;
    try {
      const res = await getSecurityResults(securityScanId);
      setResults(res);
      setState("done");
    } catch {
      setState("not_available");
    }
  }, [securityScanId]);

  if (state === "not_available") return null;

  if (state === "loading") {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-brand" />
          <h2 className="text-lg font-bold text-ink">Security Scan</h2>
        </div>
        <div className="h-32 animate-shimmer rounded-xl" />
      </div>
    );
  }

  if (state === "scanning" && securityScanId) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-brand" />
          <h2 className="text-lg font-bold text-ink">Security Scan</h2>
        </div>
        <SecurityScanProgressView scanId={securityScanId} onComplete={handleScanComplete} />
      </div>
    );
  }

  if (state !== "done" || !results) return null;

  const allFindings = results.categories?.flatMap((c) => c.findings) ?? [];
  const criticalCount = allFindings.filter((f) => f.severity === "critical").length;
  const highCount = allFindings.filter((f) => f.severity === "high").length;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-brand" />
          <h2 className="text-lg font-bold text-ink">Security Scan Results</h2>
        </div>
        {securityScanId && (
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => downloadSecurityReport(securityScanId, "json")}>
              <Download className="w-3.5 h-3.5" /> JSON
            </Button>
            <Button variant="secondary" size="sm" onClick={() => downloadSecurityReport(securityScanId, "pdf")}>
              <Download className="w-3.5 h-3.5" /> PDF
            </Button>
          </motion.div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SecurityStatCard
          label="Security Score"
          value={Math.round(results.security_score)}
          icon={ShieldCheck}
          color={results.security_score >= 80 ? "bg-green-500/10 text-green-400" : results.security_score >= 60 ? "bg-yellow-500/10 text-yellow-400" : "bg-red-500/10 text-red-400"}
          delay={0}
        />
        <SecurityStatCard label="Total Findings" value={results.total_findings} icon={AlertTriangle} color="bg-orange-500/10 text-orange-400" delay={0.1} />
        <SecurityStatCard label="Critical Issues" value={criticalCount} icon={ShieldAlert} color="bg-red-500/10 text-red-400" delay={0.2} />
        <SecurityStatCard label="High Issues" value={highCount} icon={AlertTriangle} color="bg-orange-500/10 text-orange-400" delay={0.3} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="flex flex-col items-center justify-center py-8" hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Security Score</h2>
          <SecurityScoreGauge score={Math.round(results.security_score)} />
        </Card>
        <Card hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Severity Breakdown</h2>
          <SeverityPie findings={allFindings} />
        </Card>
      </div>

      {results.categories && results.categories.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-muted mb-4">Category Scores</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.categories.map((cat, i) => (
              <motion.div
                key={cat.name}
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * i }}
                whileHover={{ y: -2, boxShadow: "0 12px 40px rgba(108,142,255,0.06)" }}
                className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg p-5"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-ink">{cat.name}</span>
                  <span className={clsx("text-xl font-bold tabular-nums", cat.score >= 80 ? "text-green-400" : cat.score >= 60 ? "text-yellow-400" : "text-red-400")}>
                    {cat.score}
                  </span>
                </div>
                <div className="w-full bg-white/[0.06] rounded-full h-1.5">
                  <motion.div
                    className="h-1.5 rounded-full"
                    style={{ background: cat.score >= 80 ? "#4ade80" : cat.score >= 60 ? "#ffd43b" : "#ff5c5c" }}
                    initial={{ width: 0 }}
                    animate={{ width: `${cat.score}%` }}
                    transition={{ duration: 1, delay: 0.2 + i * 0.1, ease: "easeOut" }}
                  />
                </div>
                <p className="text-xs text-muted mt-2">{cat.findings.length} finding{cat.findings.length !== 1 ? "s" : ""}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {allFindings.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-muted mb-4">Detailed Findings ({allFindings.length})</h2>
          <div className="space-y-6">
            {results.categories.map((cat) => (
              <motion.div key={cat.name} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-brand">{cat.name}</span>
                  <div className="flex-1 h-px bg-white/[0.06]" />
                  <span className="text-xs text-muted">{cat.findings.length} issue{cat.findings.length !== 1 ? "s" : ""}</span>
                </div>
                {cat.findings.length > 0 ? (
                  <div className="space-y-2">
                    {cat.findings.map((finding, fi) => (
                      <FindingCard key={finding.id} finding={finding} index={fi} />
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted/50 py-3 text-center">No issues found</p>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
