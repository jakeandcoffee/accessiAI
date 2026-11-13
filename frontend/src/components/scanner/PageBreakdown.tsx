import { motion } from "framer-motion";
import { FileText, Layers, XCircle } from "lucide-react";
import { clsx } from "clsx";
import type { PageResult, Violation } from "../../types";

export const ALL_PAGES = "__all__";

interface PageBreakdownProps {
  pages: PageResult[];
  violations: Violation[];
  selectedPage: string;
  onSelectPage: (page: string) => void;
}

function scoreColor(score: number) {
  if (score >= 90) return "text-green-400";
  if (score >= 75) return "text-emerald-400";
  if (score >= 50) return "text-yellow-400";
  return "text-red-400";
}

export function PageBreakdown({
  pages,
  violations,
  selectedPage,
  onSelectPage,
}: PageBreakdownProps) {
  const defaultUrl = pages[0]?.url ?? "";
  const counts: Record<string, { total: number; critical: number }> = {};
  for (const v of violations) {
    const page = v.page_url || defaultUrl;
    counts[page] ??= { total: 0, critical: 0 };
    counts[page].total++;
    if (v.impact === "critical") counts[page].critical++;
  }
  const completed = pages.filter((p) => p.status === "completed").length;

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold text-ink">
          Pages Scanned ({pages.length})
        </h2>
        <span className="text-xs text-muted">
          {completed} of {pages.length} scanned successfully
        </span>
      </div>
      <div
        className="space-y-2"
        role="group"
        aria-label="Filter results by page"
      >
        {pages.length > 1 && (
          <button
            type="button"
            onClick={() => onSelectPage(ALL_PAGES)}
            aria-pressed={selectedPage === ALL_PAGES}
            className={clsx(
              "w-full flex items-center gap-3 rounded-lg border px-4 py-3 text-left transition-colors",
              selectedPage === ALL_PAGES
                ? "border-brand/50 bg-brand/10"
                : "border-white/[0.06] hover:bg-white/[0.03]",
            )}
          >
            <Layers className="w-4 h-4 text-brand shrink-0" />
            <span className="text-sm font-semibold text-ink flex-1">
              All pages
            </span>
            <span className="text-xs text-muted">
              {violations.length} issues
            </span>
          </button>
        )}

        {pages.map((page, i) => {
          const isSelected = selectedPage === page.url;
          const failed = page.status === "failed";
          const pageCounts = counts[page.url] ?? { total: 0, critical: 0 };
          return (
            <motion.button
              key={page.url}
              type="button"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
              onClick={() => onSelectPage(page.url)}
              aria-pressed={isSelected}
              className={clsx(
                "w-full flex items-center gap-3 rounded-lg border px-4 py-3 text-left transition-colors",
                isSelected
                  ? "border-brand/50 bg-brand/10"
                  : "border-white/[0.06] hover:bg-white/[0.03]",
              )}
            >
              {failed ? (
                <XCircle className="w-4 h-4 text-red-400 shrink-0" />
              ) : (
                <FileText className="w-4 h-4 text-muted shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-mono text-ink truncate">
                  <span className="text-muted mr-2">{i + 1}.</span>
                  {page.url}
                </p>
                {failed && (
                  <p className="text-xs text-red-400 truncate mt-0.5">
                    Could not be scanned{page.error ? `: ${page.error}` : ""}
                  </p>
                )}
              </div>
              {!failed && (
                <>
                  {pageCounts.critical > 0 && (
                    <span className="text-xs text-red-400 whitespace-nowrap">
                      {pageCounts.critical} critical
                    </span>
                  )}
                  <span className="text-xs text-muted whitespace-nowrap">
                    {pageCounts.total} issues
                  </span>
                  {page.score !== null && (
                    <span
                      className={clsx(
                        "text-lg font-bold tabular-nums w-12 text-right",
                        scoreColor(page.score),
                      )}
                    >
                      {Math.round(page.score)}
                    </span>
                  )}
                </>
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
