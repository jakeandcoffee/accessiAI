import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Download } from "lucide-react";
import { useScan, useViolations } from "../hooks/useScans";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { ScanProgress } from "../components/scanner/ScanProgress";
import { ScanResultsSummary } from "../components/scanner/ScanResults";
import { ALL_PAGES, PageBreakdown } from "../components/scanner/PageBreakdown";
import { ViolationList } from "../components/violations/ViolationList";
import { SecuritySection } from "../components/security/SecuritySection";
import { CardSkeleton } from "../components/common/Skeleton";
import { downloadReport } from "../services/scanService";

export function ScanResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: scan, isLoading: loadingScan } = useScan(id!);
  // Violations are only committed when the scan finishes; fetching earlier
  // would cache an empty list that never refreshes.
  const { data: violations, isLoading: loadingViolations } = useViolations(
    id!,
    scan?.status === "completed",
  );
  const [selectedPage, setSelectedPage] = useState(ALL_PAGES);

  const pages = useMemo(() => scan?.page_results ?? [], [scan?.page_results]);
  const isMultiPage = pages.length > 1;
  const defaultPageUrl = pages[0]?.url ?? "";
  const pageOrder = useMemo(() => pages.map((p) => p.url), [pages]);
  const selectedResult = pages.find((p) => p.url === selectedPage);

  const visibleViolations = useMemo(() => {
    const all = violations ?? [];
    if (selectedPage === ALL_PAGES) return all;
    return all.filter((v) => (v.page_url || defaultPageUrl) === selectedPage);
  }, [violations, selectedPage, defaultPageUrl]);

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
              <span className="mx-2 text-muted/40">·</span>
              {scan.scan_mode === "all" ? "Scan all (discovered pages)" : "Scan (entered pages)"}
              {pages.length > 0 && ` · ${pages.length} page${pages.length === 1 ? "" : "s"}`}
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
          scanMode={scan.scan_mode}
        />
      )}

      {scan.status === "failed" && pages.length > 0 && (
        <Card hoverable={false}>
          <PageBreakdown
            pages={pages}
            violations={[]}
            selectedPage={selectedPage}
            onSelectPage={setSelectedPage}
          />
        </Card>
      )}

      {scan.status === "completed" && (
        <>
          <Card hoverable={false}>
            {isMultiPage && (
              <p className="text-center text-sm text-muted mb-4">
                {selectedResult ? (
                  <>Score for <span className="font-mono text-ink">{selectedResult.url}</span></>
                ) : (
                  <>Overall score across {pages.length} pages</>
                )}
              </p>
            )}
            {selectedResult?.status === "failed" ? (
              <p className="text-center text-red-400 py-8">
                This page could not be scanned{selectedResult.error ? `: ${selectedResult.error}` : "."}
              </p>
            ) : (
              <ScanResultsSummary
                key={selectedPage}
                score={selectedResult?.score ?? scan.accessibility_score ?? 0}
                violations={visibleViolations}
              />
            )}
          </Card>

          {pages.length > 0 && (
            <Card hoverable={false}>
              <PageBreakdown
                pages={pages}
                violations={violations ?? []}
                selectedPage={selectedPage}
                onSelectPage={setSelectedPage}
              />
            </Card>
          )}

          <div>
            <h2 className="text-lg font-bold text-ink mb-4">
              Violations ({visibleViolations.length})
            </h2>
            {loadingViolations ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-20 animate-shimmer rounded-xl" />
                ))}
              </div>
            ) : (
              <ViolationList
                violations={visibleViolations}
                pageOrder={isMultiPage && selectedPage === ALL_PAGES ? pageOrder : undefined}
                defaultPageUrl={defaultPageUrl}
              />
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
