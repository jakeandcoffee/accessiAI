from uuid import UUID

import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.models.violation import Violation
from app.models.website import Website
from app.schemas.scan import (
    ScanReportResponse,
    ScanResponse,
    SecurityCategoryResponse,
    SecurityFindingResponse,
    SecurityResultsResponse,
    ViolationResponse,
)
from app.services.security_scan_service import get_results as get_security_results
from app.services.security_scan_service import get_security_scan_id

router = APIRouter(tags=["Reports"])


def _build_security_response(scan_id: str) -> SecurityResultsResponse | None:
    sec_id = get_security_scan_id(scan_id)
    if not sec_id:
        return None
    results = get_security_results(sec_id)
    if not results or results.get("status") != "completed":
        return None
    categories = []
    for cat in results.get("categories", []):
        findings = [SecurityFindingResponse(**f) for f in cat.get("findings", [])]
        categories.append(SecurityCategoryResponse(name=cat["name"], score=cat["score"], findings=findings))
    return SecurityResultsResponse(
        security_score=results.get("security_score", 0),
        total_findings=results.get("total_findings", 0),
        categories=categories,
    )


async def _get_scan_with_violations(scan_id: UUID, user: User, db: AsyncSession):
    result = await db.execute(
        select(Scan)
        .join(Website)
        .where(Scan.id == scan_id, Website.user_id == user.id)
        .options(selectinload(Scan.website))
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    violations_result = await db.execute(
        select(Violation)
        .where(Violation.scan_id == scan_id)
        .options(selectinload(Violation.affected_elements), selectinload(Violation.ai_analyses))
        .order_by(Violation.created_at)
    )
    violations = violations_result.scalars().all()

    severity_breakdown: dict[str, int] = {}
    for v in violations:
        severity_breakdown[v.impact] = severity_breakdown.get(v.impact, 0) + 1

    return scan, violations, severity_breakdown


@router.get("/scans/{scan_id}/report", response_model=ScanReportResponse)
async def get_report_json(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scan, violations, severity_breakdown = await _get_scan_with_violations(scan_id, current_user, db)
    return ScanReportResponse(
        scan=ScanResponse.model_validate(scan),
        website_url=scan.website.url,
        website_name=scan.website.name,
        violations=[ViolationResponse.model_validate(v) for v in violations],
        severity_breakdown=severity_breakdown,
        security_results=_build_security_response(str(scan_id)),
    )


@router.get("/scans/{scan_id}/report/pdf")
async def get_report_pdf(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scan, violations, severity_breakdown = await _get_scan_with_violations(scan_id, current_user, db)

    sec_id = get_security_scan_id(str(scan_id))
    security_data = None
    if sec_id:
        security_data = get_security_results(sec_id)
        if security_data and security_data.get("status") != "completed":
            security_data = None

    from app.services.report_service import generate_pdf_report
    pdf_buffer = generate_pdf_report(scan, violations, severity_breakdown, security_data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=accessiai-report-{scan_id}.pdf"},
    )


@router.get("/scans/{scan_id}/report/markdown")
async def get_report_markdown(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scan, violations, severity_breakdown = await _get_scan_with_violations(scan_id, current_user, db)

    sec_id = get_security_scan_id(str(scan_id))
    security_data = None
    if sec_id:
        security_data = get_security_results(sec_id)
        if security_data and security_data.get("status") != "completed":
            security_data = None

    from app.services.report_service import generate_markdown_report
    md = generate_markdown_report(scan, violations, severity_breakdown, security_data)

    return PlainTextResponse(
        md,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=accessiai-report-{scan_id}.md"},
    )
