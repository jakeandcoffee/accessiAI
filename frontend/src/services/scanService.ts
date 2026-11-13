import api from "./api";
import type { Scan, ScanMode, Violation, AIAnalysis, DashboardData } from "../types";

export async function triggerScan({
  websiteId,
  mode = "entered",
}: {
  websiteId: string;
  mode?: ScanMode;
}): Promise<Scan> {
  const { data } = await api.post<Scan>(`/api/websites/${websiteId}/scans`, null, {
    params: { mode },
  });
  return data;
}

export async function getScan(scanId: string): Promise<Scan> {
  const { data } = await api.get<Scan>(`/api/scans/${scanId}`);
  return data;
}

export async function getScans(websiteId: string): Promise<Scan[]> {
  const { data } = await api.get<Scan[]>(`/api/websites/${websiteId}/scans`);
  return data;
}

export async function getViolations(scanId: string): Promise<Violation[]> {
  const { data } = await api.get<Violation[]>(`/api/scans/${scanId}/violations`);
  return data;
}

export async function requestAIAnalysis(violationId: string): Promise<AIAnalysis> {
  const { data } = await api.post<AIAnalysis>(`/api/violations/${violationId}/ai-analysis`);
  return data;
}

export async function updateViolationStatus(
  violationId: string,
  status: string,
): Promise<Violation> {
  const { data } = await api.patch<Violation>(`/api/violations/${violationId}/status`, { status });
  return data;
}

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await api.get<DashboardData>("/api/dashboard");
  return data;
}

export async function downloadReport(scanId: string, format: "pdf" | "json" | "md"): Promise<void> {
  const pathMap = {
    pdf: `/api/scans/${scanId}/report/pdf`,
    json: `/api/scans/${scanId}/report`,
    md: `/api/scans/${scanId}/report/markdown`,
  };
  const response = await api.get(pathMap[format], {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = `accessibility-report-${scanId}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
