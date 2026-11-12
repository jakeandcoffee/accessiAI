from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.models.violation import Violation
from app.models.website import Website

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total websites
    websites_result = await db.execute(
        select(func.count(Website.id)).where(Website.user_id == current_user.id)
    )
    total_websites = websites_result.scalar() or 0

    # Total scans
    scans_result = await db.execute(
        select(func.count(Scan.id))
        .join(Website)
        .where(Website.user_id == current_user.id)
    )
    total_scans = scans_result.scalar() or 0

    # Total violations
    violations_result = await db.execute(
        select(func.count(Violation.id))
        .join(Scan)
        .join(Website)
        .where(Website.user_id == current_user.id)
    )
    total_violations = violations_result.scalar() or 0

    # Average accessibility score
    score_result = await db.execute(
        select(func.avg(Scan.accessibility_score))
        .join(Website)
        .where(Website.user_id == current_user.id, Scan.status == "completed")
    )
    accessibility_score = score_result.scalar() or 0

    # Severity breakdown
    severity_result = await db.execute(
        select(Violation.impact, func.count(Violation.id))
        .join(Scan)
        .join(Website)
        .where(Website.user_id == current_user.id)
        .group_by(Violation.impact)
    )
    severity_breakdown = [
        {"severity": row[0], "count": row[1]}
        for row in severity_result.all()
    ]

    # Recent scans (last 10)
    recent_result = await db.execute(
        select(Scan)
        .join(Website)
        .where(Website.user_id == current_user.id)
        .options(selectinload(Scan.website))
        .order_by(Scan.scan_started_at.desc())
        .limit(10)
    )
    recent_scans = [
        {
            "id": str(s.id),
            "website_id": str(s.website_id),
            "website_name": s.website.name if s.website else None,
            "website_url": s.website.url if s.website else None,
            "status": s.status,
            "accessibility_score": s.accessibility_score,
            "total_violations": s.total_violations,
            "scan_started_at": s.scan_started_at.isoformat(),
            "scan_completed_at": s.scan_completed_at.isoformat() if s.scan_completed_at else None,
        }
        for s in recent_result.scalars().all()
    ]

    # Score history (completed scans over time)
    history_result = await db.execute(
        select(Scan)
        .join(Website)
        .where(Website.user_id == current_user.id, Scan.status == "completed")
        .options(selectinload(Scan.website))
        .order_by(Scan.scan_started_at.asc())
        .limit(30)
    )
    score_history = [
        {
            "date": s.scan_started_at.isoformat(),
            "score": round(s.accessibility_score, 1) if s.accessibility_score else 0,
            "website_name": s.website.name if s.website else "",
        }
        for s in history_result.scalars().all()
    ]

    return {
        "total_websites": total_websites,
        "total_scans": total_scans,
        "total_violations": total_violations,
        "accessibility_score": round(accessibility_score, 1),
        "severity_breakdown": severity_breakdown,
        "recent_scans": recent_scans,
        "score_history": score_history,
    }
