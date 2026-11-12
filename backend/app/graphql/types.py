from datetime import datetime
from uuid import UUID

import strawberry


@strawberry.type
class SeverityBreakdown:
    severity: str
    count: int


@strawberry.type
class RecentScan:
    id: UUID
    website_url: str
    website_name: str
    score: float | None
    scan_date: datetime
    total_violations: int


@strawberry.type
class Dashboard:
    total_websites: int
    total_scans: int
    total_violations: int
    accessibility_score: float | None
    severity_breakdown: list[SeverityBreakdown]
    recent_scans: list[RecentScan]


@strawberry.type
class AffectedElementNode:
    id: UUID
    selector: str
    html: str
    failure_summary: str | None


@strawberry.type
class AIAnalysisNode:
    id: UUID
    explanation: str
    suggested_fix: str
    model_name: str
    created_at: datetime


@strawberry.type
class ViolationNode:
    id: UUID
    rule_id: str
    description: str
    impact: str
    wcag_criteria: str
    status: str
    help_url: str | None
    created_at: datetime
    affected_elements: list[AffectedElementNode]
    ai_analyses: list[AIAnalysisNode]
