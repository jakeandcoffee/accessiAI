import { motion } from "framer-motion";
import { AlertTriangle, AlertCircle, Info, CheckCircle } from "lucide-react";
import { ScoreGauge } from "../dashboard/ScoreGauge";
import type { Violation } from "../../types";

interface ScanResultsProps {
  score: number;
  violations: Violation[];
}

function countBySeverity(violations: Violation[]) {
  const counts = { critical: 0, serious: 0, moderate: 0, minor: 0 };
  for (const v of violations) {
    counts[v.impact]++;
  }
  return counts;
}

const severityConfig = [
  { key: "critical" as const, label: "Critical", icon: AlertCircle, color: "text-red-400", bg: "bg-red-500/10 border border-red-500/20" },
  { key: "serious" as const, label: "Serious", icon: AlertTriangle, color: "text-orange-400", bg: "bg-orange-500/10 border border-orange-500/20" },
  { key: "moderate" as const, label: "Moderate", icon: Info, color: "text-yellow-400", bg: "bg-yellow-500/10 border border-yellow-500/20" },
  { key: "minor" as const, label: "Minor", icon: CheckCircle, color: "text-blue-400", bg: "bg-blue-500/10 border border-blue-500/20" },
];

export function ScanResultsSummary({ score, violations }: ScanResultsProps) {
  const counts = countBySeverity(violations);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center"
    >
      <div className="relative mb-8">
        <ScoreGauge score={score} size={200} />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-lg">
        {severityConfig.map((s, i) => (
          <motion.div
            key={s.key}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 + i * 0.1 }}
            className={`rounded-xl p-4 text-center ${s.bg}`}
          >
            <s.icon className={`w-5 h-5 mx-auto mb-1 ${s.color}`} />
            <div className={`text-2xl font-bold tabular-nums ${s.color}`}>
              {counts[s.key]}
            </div>
            <div className="text-xs text-muted">{s.label}</div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
