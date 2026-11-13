import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, ExternalLink, Calendar, Radar, FileText, Pencil } from "lucide-react";
import { useWebsite } from "../hooks/useWebsites";
import { useScans } from "../hooks/useScans";
import { Card } from "../components/common/Card";
import { Badge } from "../components/common/Badge";
import { ScanButton } from "../components/websites/ScanButton";
import { ScoreGauge } from "../components/dashboard/ScoreGauge";
import { CardSkeleton } from "../components/common/Skeleton";
import { Button } from "../components/common/Button";
import { ManagePagesModal } from "../components/websites/ManagePagesModal";

export function WebsiteDetails() {
  const { id } = useParams<{ id: string }>();
  const { data: website, isLoading: loadingWebsite } = useWebsite(id!);
  const { data: scans, isLoading: loadingScans } = useScans(id!);
  const [isPagesOpen, setIsPagesOpen] = useState(false);

  if (loadingWebsite) {
    return (
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  if (!website) {
    return <p className="text-muted text-center py-12">Website not found</p>;
  }

  const pageList = Array.from(new Set([website.url, ...(website.page_urls ?? [])]));

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <Link
          to="/websites"
          className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Websites
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ink">{website.name}</h1>
            <a
              href={website.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-brand hover:underline mt-1"
            >
              {website.url} <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
          <ScanButton websiteId={website.id} />
        </div>
      </motion.div>

      <Card hoverable={false}>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-muted flex items-center gap-1.5">
            <FileText className="w-4 h-4" /> Pages Scanned ({pageList.length})
          </h2>
          <Button variant="secondary" size="sm" onClick={() => setIsPagesOpen(true)}>
            <Pencil className="w-3.5 h-3.5" /> Edit Pages
          </Button>
        </div>
        <ul className="space-y-1">
          {pageList.map((url) => (
            <li key={url} className="text-sm font-mono text-ink truncate">{url}</li>
          ))}
        </ul>
      </Card>

      <ManagePagesModal
        website={website}
        isOpen={isPagesOpen}
        onClose={() => setIsPagesOpen(false)}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="flex flex-col items-center justify-center py-8" hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Current Score</h2>
          <ScoreGauge
            score={website.latest_score !== null ? Math.round(website.latest_score) : 0}
            size={160}
          />
        </Card>

        <Card className="lg:col-span-2" hoverable={false}>
          <h2 className="text-sm font-semibold text-muted mb-4">Scan History</h2>
          {loadingScans ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-14 animate-shimmer rounded-lg" />
              ))}
            </div>
          ) : scans && scans.length > 0 ? (
            <div className="space-y-2">
              {scans.map((scan, i) => (
                <motion.div
                  key={scan.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link
                    to={`/scans/${scan.id}`}
                    className="flex items-center justify-between rounded-lg border border-white/[0.06] p-4 hover:bg-white/[0.03] transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Radar className="w-4 h-4 text-muted" />
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              scan.status === "completed"
                                ? "resolved"
                                : scan.status === "failed"
                                  ? "critical"
                                  : "open"
                            }
                          >
                            {scan.status}
                          </Badge>
                          <span className="text-sm text-ink">
                            {scan.total_violations} violations
                          </span>
                        </div>
                        <span className="text-xs text-muted flex items-center gap-1 mt-0.5">
                          <Calendar className="w-3 h-3" />
                          {new Date(scan.scan_started_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    {scan.accessibility_score !== null && (
                      <span className="text-lg font-bold tabular-nums text-ink">
                        {Math.round(scan.accessibility_score)}
                      </span>
                    )}
                  </Link>
                </motion.div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted text-sm py-8">
              No scans yet. Click "Scan" to get started.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
