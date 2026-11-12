import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "../common/Badge";
import type { Scan } from "../../types";

interface RecentScansProps {
  scans: Scan[];
}

export function RecentScans({ scans }: RecentScansProps) {
  return (
    <div className="space-y-2">
      {scans.map((scan, i) => (
        <motion.div
          key={scan.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 * i, type: "spring", stiffness: 300, damping: 24 }}
        >
          <Link
            to={`/scans/${scan.id}`}
            className="flex items-center justify-between rounded-lg border border-white/[0.06] p-4 hover:bg-white/[0.03] transition-colors group"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm text-ink truncate">
                  {scan.website_name || scan.website_url}
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <span className="text-xs text-muted">
                {new Date(scan.scan_started_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className="flex items-center gap-3">
              {scan.accessibility_score !== null && (
                <span className="text-sm font-bold tabular-nums text-ink">
                  {Math.round(scan.accessibility_score)}
                </span>
              )}
              <Badge variant={scan.status === "completed" ? "resolved" : scan.status === "failed" ? "critical" : "open"}>
                {scan.status}
              </Badge>
            </div>
          </Link>
        </motion.div>
      ))}
    </div>
  );
}
