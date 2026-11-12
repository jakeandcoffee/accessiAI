import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import { ViolationList } from "../components/violations/ViolationList";
import { EmptyState } from "../components/common/EmptyState";
import { AlertTriangle } from "lucide-react";
import type { Violation } from "../types";
import { CardSkeleton } from "../components/common/Skeleton";

export function Violations() {
  const { data: violations, isLoading } = useQuery({
    queryKey: ["all-violations"],
    queryFn: async () => {
      const { data } = await api.get<Violation[]>("/api/violations");
      return data;
    },
  });

  return (
    <div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-6">
        <h1 className="text-2xl font-bold text-ink">All Violations</h1>
        <p className="text-sm text-muted mt-1">
          View and manage accessibility issues across all websites
        </p>
      </motion.div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : violations && violations.length > 0 ? (
        <ViolationList violations={violations} />
      ) : (
        <EmptyState
          icon={AlertTriangle}
          title="No violations found"
          description="Run a scan on one of your websites to discover accessibility issues."
        />
      )}
    </div>
  );
}
