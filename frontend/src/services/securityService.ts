import api from "./api";

export interface SecurityFinding {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  category: string;
  recommendation: string;
  details: string;
}

export interface SecurityCategory {
  name: string;
  score: number;
  findings: SecurityFinding[];
}

export interface SecurityScanResults {
  scan_id: string;
  url: string;
  status: string;
  security_score: number;
  total_findings: number;
  scan_started_at: string;
  scan_completed_at: string;
  categories: SecurityCategory[];
}

export async function startSecurityScan(
  url: string,
): Promise<{ scan_id: string; status: string }> {
  const { data } = await api.post("/api/security-scan", { url });
  return data;
}

export async function getSecurityResults(
  scanId: string,
): Promise<SecurityScanResults> {
  const { data } = await api.get(`/api/security-scan/${scanId}/results`);
  return data;
}

export async function downloadSecurityReport(
  scanId: string,
  format: "pdf" | "json",
): Promise<void> {
  const path =
    format === "pdf"
      ? `/api/security-scan/${scanId}/report/pdf`
      : `/api/security-scan/${scanId}/report/json`;
  const response = await api.get(path, { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = `security-report-${scanId}.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
