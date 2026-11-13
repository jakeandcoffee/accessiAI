import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FileText, Download, Trash2 } from "lucide-react";
import api from "../services/api";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { EmptyState } from "../components/common/EmptyState";
import { CardSkeleton } from "../components/common/Skeleton";
import { downloadReport } from "../services/scanService";
import type { Scan } from "../types";

export function Reports() {
  const queryClient = useQueryClient();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { data: scans, isLoading } = useQuery({
    queryKey: ["completed-scans"],
    queryFn: async () => {
      const { data } = await api.get<Scan[]>("/api/scans?status=completed");
      return data;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (scanId: string) => {
      await api.delete(`/api/scans/${scanId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["completed-scans"] });
      queryClient.invalidateQueries({ queryKey: ["scans"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      setDeletingId(null);
    },
  });

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-6">
        <h1 className="text-2xl font-bold text-ink">Reports</h1>
        <p className="text-sm text-muted mt-1">Download accessibility reports for your scans</p>
      </motion.div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : scans && scans.length > 0 ? (
        <div className="space-y-3">
          {scans.map((scan, i) => (
            <motion.div
              key={scan.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-brand/10 border border-brand/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-brand" />
                  </div>
                  <div>
                    <p className="font-medium text-sm text-ink">
                      {scan.website_name || "Scan Report"}
                    </p>
                    <p className="text-xs text-muted">
                      {new Date(scan.scan_started_at).toLocaleDateString()} ·{" "}
                      {scan.total_violations} violations
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {scan.accessibility_score !== null && (
                    <Badge variant={scan.accessibility_score >= 75 ? "resolved" : scan.accessibility_score >= 50 ? "moderate" : "critical"}>
                      Score: {Math.round(scan.accessibility_score)}
                    </Badge>
                  )}
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => downloadReport(scan.id, "json", scan.website_name)}
                  >
                    <Download className="w-3.5 h-3.5" /> JSON
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => downloadReport(scan.id, "pdf", scan.website_name)}
                  >
                    <Download className="w-3.5 h-3.5" /> PDF
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => downloadReport(scan.id, "md", scan.website_name)}
                  >
                    <Download className="w-3.5 h-3.5" /> MD
                  </Button>
                  <AnimatePresence mode="wait">
                    {deletingId === scan.id ? (
                      <motion.div
                        key="confirm"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="flex items-center gap-1.5"
                      >
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setDeletingId(null)}
                        >
                          Cancel
                        </Button>
                        <button
                          className="px-2.5 py-1.5 text-xs font-medium rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors disabled:opacity-50"
                          onClick={() => deleteMutation.mutate(scan.id)}
                          disabled={deleteMutation.isPending}
                        >
                          {deleteMutation.isPending ? "Deleting…" : "Confirm"}
                        </button>
                      </motion.div>
                    ) : (
                      <motion.div key="delete" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                        <button
                          className="p-1.5 rounded-lg text-muted hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          onClick={() => setDeletingId(scan.id)}
                          title="Delete report"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FileText}
          title="No reports available"
          description="Complete a scan to generate downloadable accessibility reports."
        />
      )}
    </div>
  );
}
