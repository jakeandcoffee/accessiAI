import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Download } from "lucide-react";
import { useScan, useViolations } from "../hooks/useScans";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { ScanProgress } from "../components/scanner/ScanProgress";
import { ScanResultsSummary } from "../components/scanner/ScanResults";
import { ViolationList } from "../components/violations/ViolationList";
import { SecuritySection } from "../components/security/SecuritySection";
import { CardSkeleton } from "../components/common/Skeleton";
import { downloadReport } from "../services/scanService";

export function ScanResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: scan, isLoading: loadingScan } = useScan(id!);
  const { data: violations, isLoading: loadingViolations } = useViolations(id!);

  if (loadingScan) {
    return (
      <div className="space-y-4">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  if (!scan) {
    return <p className="text-muted text-center py-12">Scan not found</p>;
  }

  const isRunning = scan.status === "pending" || scan.status === "running";

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <Link
          to={`/websites/${scan.website_id}`}
          className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Website
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ink">Scan Results</h1>
            <p className="text-sm text-muted mt-1">
              {new Date(scan.scan_started_at).toLocaleString()}
            </p>
          </div>
          {scan.status === "completed" && (
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => downloadReport(scan.id, "json")}
              >
                <Download className="w-4 h-4" /> JSON
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => downloadReport(scan.id, "pdf")}
              >
                <Download className="w-4 h-4" /> PDF
              </Button>
            </div>
          )}
        </div>
      </motion.div>

      {isRunning && (
        <ScanProgress
          scanId={scan.id}
          status={scan.status}
          startedAt={scan.scan_started_at}
        />
      )}

      {scan.status === "completed" && (
        <>
          <Card hoverable={false}>
            <ScanResultsSummary
              score={scan.accessibility_score ?? 0}
              violations={violations ?? []}
            />
          </Card>

          <div>
            <h2 className="text-lg font-bold text-ink mb-4">
              Violations ({violations?.length ?? 0})
            </h2>
            {loadingViolations ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-20 animate-shimmer rounded-xl" />
                ))}
              </div>
            ) : (
              <ViolationList violations={violations ?? []} />
            )}
          </div>
        </>
      )}

      {(isRunning || scan.status === "completed") && (
        <SecuritySection scanId={scan.id} />
      )}

      {scan.status === "failed" && (
        <Card hoverable={false}>
          <div className="text-center py-8">
            <p className="text-red-400 font-medium">Scan failed</p>
            <p className="text-sm text-muted mt-1">
              The scan could not be completed. The website may be unreachable or blocked.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
