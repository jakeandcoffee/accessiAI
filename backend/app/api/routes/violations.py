from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.models.violation import Violation
from app.models.website import Website
from app.schemas.scan import ViolationResponse, ViolationStatusUpdate

router = APIRouter(tags=["Violations"])


@router.get("/scans/{scan_id}/violations", response_model=list[ViolationResponse])
async def list_violations(
    scan_id: UUID,
    impact: str | None = Query(None),
    violation_status: str | None = Query(None, alias="status"),
    wcag: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scan_result = await db.execute(
        select(Scan).join(Website).where(Scan.id == scan_id, Website.user_id == current_user.id)
    )
    if not scan_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    query = (
        select(Violation)
        .where(Violation.scan_id == scan_id)
        .options(selectinload(Violation.affected_elements), selectinload(Violation.ai_analyses))
    )

    if impact:
        query = query.where(Violation.impact == impact)
    if violation_status:
        query = query.where(Violation.status == violation_status)
    if wcag:
        query = query.where(Violation.wcag_criteria.contains(wcag))

    result = await db.execute(query.order_by(Violation.created_at.desc()))
    return [ViolationResponse.model_validate(v) for v in result.scalars().all()]


@router.patch("/violations/{violation_id}/status", response_model=ViolationResponse)
async def update_violation_status(
    violation_id: UUID,
    data: ViolationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    valid_statuses = {"open", "in_progress", "resolved", "ignored"}
    if data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(valid_statuses)}",
        )

    result = await db.execute(
        select(Violation)
        .join(Scan)
        .join(Website)
        .where(Violation.id == violation_id, Website.user_id == current_user.id)
        .options(selectinload(Violation.affected_elements), selectinload(Violation.ai_analyses))
    )
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")

    violation.status = data.status
    await db.flush()
    return ViolationResponse.model_validate(violation)


@router.post("/violations/{violation_id}/ai-analysis", response_model=ViolationResponse)
async def request_ai_analysis(
    violation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Violation)
        .join(Scan)
        .join(Website)
        .where(Violation.id == violation_id, Website.user_id == current_user.id)
        .options(selectinload(Violation.affected_elements), selectinload(Violation.ai_analyses))
    )
    violation = result.scalar_one_or_none()
    if not violation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Violation not found")

    scan = await db.get(Scan, violation.scan_id)
    guidelines = None
    if scan:
        website = await db.get(Website, scan.website_id)
        if website and website.attachments:
            from app.services.scan_service import _extract_attachment_text
            guidelines = _extract_attachment_text(str(website.id), website.attachments)

    from app.services.ai_service import analyze_violation
    await analyze_violation(violation, db, guidelines=guidelines or None)

    await db.refresh(violation, attribute_names=["ai_analyses"])
    return ViolationResponse.model_validate(violation)
