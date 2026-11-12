import { motion } from "framer-motion";
import { Globe, Radar, AlertTriangle, TrendingUp } from "lucide-react";
import { useDashboard } from "../hooks/useScans";
import { StatsCard } from "../components/common/StatsCard";
import { CardSkeleton } from "../components/common/Skeleton";
import { Card } from "../components/common/Card";
import { ScoreGauge } from "../components/dashboard/ScoreGauge";
import { SeverityChart } from "../components/dashboard/SeverityChart";
import { ScoreHistory } from "../components/dashboard/ScoreHistory";
import { RecentScans } from "../components/dashboard/RecentScans";

export function Dashboard() {
  const { data, isLoading } = useDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  const dashboard = data ?? {
    total_websites: 0,
    total_scans: 0,
    total_violations: 0,
    accessibility_score: 0,
    severity_breakdown: [],
    recent_scans: [],
    score_history: [],
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-2xl font-bold text-ink">Dashboard</h1>
        <p className="text-sm text-muted mt-1">Overview of your accessibility audits</p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard label="Websites" value={dashboard.total_websites} icon={Globe} color="brand" delay={0} />
        <StatsCard label="Total Scans" value={dashboard.total_scans} icon={Radar} color="green" delay={0.1} />
        <StatsCard label="Violations" value={dashboard.total_violations} icon={AlertTriangle} color="orange" delay={0.2} />
        <StatsCard label="Avg Score" value={Math.round(dashboard.accessibility_score)} icon={TrendingUp} color="brand" delay={0.3} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="flex flex-col items-center justify-center py-8" hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Overall Score</h2>
          <ScoreGauge score={Math.round(dashboard.accessibility_score)} />
        </Card>

        <Card hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Severity Breakdown</h2>
          {dashboard.severity_breakdown.length > 0 ? (
            <SeverityChart data={dashboard.severity_breakdown} />
          ) : (
            <p className="text-center text-muted text-sm py-12">No data yet</p>
          )}
        </Card>

        <Card hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Score History</h2>
          {dashboard.score_history.length > 0 ? (
            <ScoreHistory data={dashboard.score_history} />
          ) : (
            <p className="text-center text-muted text-sm py-12">
              Scan some websites to see trends
            </p>
          )}
        </Card>
      </div>

      <Card hoverable={false}>
        <h2 className="text-sm font-semibold text-muted mb-4">Recent Scans</h2>
        {dashboard.recent_scans.length > 0 ? (
          <RecentScans scans={dashboard.recent_scans} />
        ) : (
          <p className="text-center text-muted text-sm py-8">No scans yet</p>
        )}
      </Card>
    </div>
  );
}
