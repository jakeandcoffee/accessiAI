import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as scanService from "../services/scanService";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: scanService.getDashboard,
  });
}

export function useScans(websiteId: string) {
  return useQuery({
    queryKey: ["scans", websiteId],
    queryFn: () => scanService.getScans(websiteId),
    enabled: !!websiteId,
  });
}

export function useScan(scanId: string) {
  return useQuery({
    queryKey: ["scan", scanId],
    queryFn: () => scanService.getScan(scanId),
    enabled: !!scanId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "pending" || status === "running" ? 3000 : false;
    },
  });
}

export function useTriggerScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: scanService.triggerScan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scans"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useViolations(scanId: string) {
  return useQuery({
    queryKey: ["violations", scanId],
    queryFn: () => scanService.getViolations(scanId),
    enabled: !!scanId,
  });
}

export function useAIAnalysis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: scanService.requestAIAnalysis,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["violations"] }),
  });
}

export function useUpdateViolationStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      scanService.updateViolationStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["violations"] }),
  });
}
