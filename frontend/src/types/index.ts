export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export interface Attachment {
  id: string;
  filename: string;
  size: number;
  content_type: string;
  uploaded_at: string;
}

export interface Website {
  id: string;
  name: string;
  url: string;
  page_urls: string[];
  attachments: Attachment[];
  created_at: string;
  latest_score: number | null;
  last_scanned: string | null;
}

export interface PageResult {
  url: string;
  status: "completed" | "failed";
  score: number | null;
  total_violations: number;
  error: string | null;
}

export type ScanMode = "entered" | "all";

export interface Scan {
  id: string;
  website_id: string;
  website_url?: string;
  website_name?: string;
  status: "pending" | "running" | "completed" | "failed";
  accessibility_score: number | null;
  total_violations: number;
  scan_started_at: string;
  scan_completed_at: string | null;
  scan_mode?: ScanMode;
  page_results?: PageResult[] | null;
}

export interface AffectedElement {
  id: string;
  violation_id: string;
  selector: string;
  html: string;
  failure_summary: string | null;
}

export interface AIAnalysis {
  id: string;
  violation_id: string;
  explanation: string;
  suggested_fix: string;
  model_name: string;
  created_at: string;
}

export interface Violation {
  id: string;
  scan_id: string;
  category: string;
  rule_id: string;
  description: string;
  impact: "critical" | "serious" | "moderate" | "minor";
  wcag_criteria: string;
  status: "open" | "in_progress" | "resolved" | "ignored";
  help_url: string | null;
  page_url?: string | null;
  created_at: string;
  affected_elements: AffectedElement[];
  ai_analyses: AIAnalysis[];
}

export interface SeverityBreakdown {
  severity: string;
  count: number;
}

export interface DashboardData {
  total_websites: number;
  total_scans: number;
  total_violations: number;
  accessibility_score: number;
  severity_breakdown: SeverityBreakdown[];
  recent_scans: Scan[];
  score_history: ScoreHistoryEntry[];
}

export interface ScoreHistoryEntry {
  date: string;
  score: number;
  website_name: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
