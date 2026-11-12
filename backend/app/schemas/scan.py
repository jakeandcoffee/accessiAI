from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScanResponse(BaseModel):
    id: UUID
    website_id: UUID
    status: str
    accessibility_score: float | None
    total_violations: int
    scan_started_at: datetime
    scan_completed_at: datetime | None
    website_name: str | None = None
    website_url: str | None = None

    model_config = {"from_attributes": True}


class AffectedElementResponse(BaseModel):
    id: UUID
    selector: str
    html: str
    failure_summary: str | None

    model_config = {"from_attributes": True}


class AIAnalysisResponse(BaseModel):
    id: UUID
    explanation: str
    suggested_fix: str
    model_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ViolationResponse(BaseModel):
    id: UUID
    scan_id: UUID
    category: str
    rule_id: str
    description: str
    impact: str
    wcag_criteria: str
    status: str
    help_url: str | None
    created_at: datetime
    affected_elements: list[AffectedElementResponse] = []
    ai_analyses: list[AIAnalysisResponse] = []

    model_config = {"from_attributes": True}


class ViolationStatusUpdate(BaseModel):
    status: str


class SecurityFindingResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    category: str
    recommendation: str
    details: str = ""


class SecurityCategoryResponse(BaseModel):
    name: str
    score: int
    findings: list[SecurityFindingResponse]


class SecurityResultsResponse(BaseModel):
    security_score: int
    total_findings: int
    categories: list[SecurityCategoryResponse]


class ScanReportResponse(BaseModel):
    scan: ScanResponse
    website_url: str
    website_name: str
    violations: list[ViolationResponse]
    severity_breakdown: dict[str, int]
    security_results: SecurityResultsResponse | None = None
