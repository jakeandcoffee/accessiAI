from uuid import UUID

import strawberry
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from strawberry.types import Info

from app.graphql.types import (
    AffectedElementNode,
    AIAnalysisNode,
    Dashboard,
    RecentScan,
    SeverityBreakdown,
    ViolationNode,
)
from app.models.scan import Scan
from app.models.violation import Violation
from app.models.website import Website


async def _get_db(info: Info):
    return info.context["db"]


async def _get_user(info: Info):
    return info.context["user"]


@strawberry.type
class Query:
    @strawberry.field
    async def dashboard(self, info: Info) -> Dashboard:
        db = await _get_db(info)
        user = await _get_user(info)

        websites_result = await db.execute(
            select(func.count(Website.id)).where(Website.user_id == user.id)
        )
        total_websites = websites_result.scalar() or 0

        scans_result = await db.execute(
            select(func.count(Scan.id))
            .join(Website)
            .where(Website.user_id == user.id)
        )
        total_scans = scans_result.scalar() or 0

        violations_result = await db.execute(
            select(func.count(Violation.id))
            .join(Scan)
            .join(Website)
            .where(Website.user_id == user.id)
        )
        total_violations = violations_result.scalar() or 0

        avg_result = await db.execute(
            select(func.avg(Scan.accessibility_score))
            .join(Website)
            .where(Website.user_id == user.id, Scan.status == "completed")
        )
        avg_score = avg_result.scalar()

        severity_result = await db.execute(
            select(Violation.impact, func.count(Violation.id))
            .join(Scan)
            .join(Website)
            .where(Website.user_id == user.id)
            .group_by(Violation.impact)
        )
        severity_breakdown = [
            SeverityBreakdown(severity=row[0], count=row[1])
            for row in severity_result.all()
        ]

        recent_result = await db.execute(
            select(Scan)
            .join(Website)
            .where(Website.user_id == user.id, Scan.status == "completed")
            .options(selectinload(Scan.website))
            .order_by(Scan.scan_completed_at.desc())
            .limit(10)
        )
        recent_scans = [
            RecentScan(
                id=s.id,
                website_url=s.website.url,
                website_name=s.website.name,
                score=s.accessibility_score,
                scan_date=s.scan_completed_at or s.scan_started_at,
                total_violations=s.total_violations,
            )
            for s in recent_result.scalars().all()
        ]

        return Dashboard(
            total_websites=total_websites,
            total_scans=total_scans,
            total_violations=total_violations,
            accessibility_score=round(avg_score, 1) if avg_score else None,
            severity_breakdown=severity_breakdown,
            recent_scans=recent_scans,
        )

    @strawberry.field
    async def violations(
        self,
        info: Info,
        website_id: UUID,
        impact: str | None = None,
        status: str | None = None,
    ) -> list[ViolationNode]:
        db = await _get_db(info)
        user = await _get_user(info)

        website_result = await db.execute(
            select(Website).where(Website.id == website_id, Website.user_id == user.id)
        )
        if not website_result.scalar_one_or_none():
            return []

        query = (
            select(Violation)
            .join(Scan)
            .where(Scan.website_id == website_id)
            .options(selectinload(Violation.affected_elements), selectinload(Violation.ai_analyses))
        )
        if impact:
            query = query.where(Violation.impact == impact)
        if status:
            query = query.where(Violation.status == status)

        result = await db.execute(query.order_by(Violation.created_at.desc()))
        violations = result.scalars().all()

        return [
            ViolationNode(
                id=v.id,
                rule_id=v.rule_id,
                description=v.description,
                impact=v.impact,
                wcag_criteria=v.wcag_criteria,
                status=v.status,
                help_url=v.help_url,
                created_at=v.created_at,
                affected_elements=[
                    AffectedElementNode(
                        id=el.id, selector=el.selector, html=el.html, failure_summary=el.failure_summary
                    )
                    for el in v.affected_elements
                ],
                ai_analyses=[
                    AIAnalysisNode(
                        id=a.id,
                        explanation=a.explanation,
                        suggested_fix=a.suggested_fix,
                        model_name=a.model_name,
                        created_at=a.created_at,
                    )
                    for a in v.ai_analyses
                ],
            )
            for v in violations
        ]
