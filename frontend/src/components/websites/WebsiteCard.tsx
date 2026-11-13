import { motion } from "framer-motion";
import { Globe, Trash2, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "../common/Button";
import { ScanButton } from "./ScanButton";
import type { Website } from "../../types";

interface WebsiteCardProps {
  website: Website;
  onDelete: (id: string) => void;
  index: number;
}

function getScoreColor(score: number | null) {
  if (score === null) return "text-muted";
  if (score < 50) return "text-red-400";
  if (score < 75) return "text-orange-400";
  return "text-green-400";
}

export function WebsiteCard({ website, onDelete, index }: WebsiteCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, type: "spring", stiffness: 300, damping: 24 }}
      whileHover={{ y: -4, boxShadow: "0 16px 48px rgba(108,142,255,0.08)" }}
      className="rounded-xl border border-white/[0.08] bg-white/[0.04] backdrop-blur-lg p-6 group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-brand/10 border border-brand/20 flex items-center justify-center">
            <Globe className="w-5 h-5 text-brand" />
          </div>
          <div>
            <Link
              to={`/websites/${website.id}`}
              className="font-semibold text-ink hover:text-brand transition-colors"
            >
              {website.name}
            </Link>
            <a
              href={website.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-muted hover:text-brand transition-colors"
            >
              {website.url}
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
        <button
          onClick={() => onDelete(website.id)}
          className="rounded-lg p-1.5 text-muted hover:text-red-400 hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100"
          aria-label={`Delete ${website.name}`}
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs text-muted block">Score</span>
          <span className={`text-2xl font-bold tabular-nums ${getScoreColor(website.latest_score)}`}>
            {website.latest_score !== null ? Math.round(website.latest_score) : "—"}
          </span>
        </div>
        <div className="text-right">
          <span className="text-xs text-muted block">Last Scan</span>
          <span className="text-sm text-ink">
            {website.last_scanned
              ? new Date(website.last_scanned).toLocaleDateString("en-US", { month: "short", day: "numeric" })
              : "Never"}
          </span>
        </div>
      </div>

      <div className="flex gap-2 mt-4 pt-4 border-t border-white/[0.06]">
        <ScanButton websiteId={website.id} className="flex-1" />
        <Button variant="secondary" size="sm" className="flex-1" asChild>
          <Link to={`/websites/${website.id}`}>Details</Link>
        </Button>
      </div>
    </motion.div>
  );
}
