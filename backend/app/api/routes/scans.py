import asyncio
import json
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.models.website import Website
from app.schemas.scan import ScanResponse
from app.services.scan_progress import get_steps, subscribe, unsubscribe

router = APIRouter(tags=["Scans"])


@router.post("/websites/{website_id}/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def trigger_scan(
    website_id: UUID,
    background_tasks: BackgroundTasks,
    mode: Literal["entered", "all"] = Query(
        "entered",
        description='"entered" scans only the URLs saved on the website; "all" also discovers and scans every same-site page',
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    scan = Scan(
        website_id=website.id,
        status="pending",
        scan_mode=mode,
        scan_started_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    await db.flush()

    from app.services.scan_service import run_scan
    background_tasks.add_task(run_scan, str(scan.id), website.scan_urls, discover=mode == "all")

    from uuid import uuid4 as uuid4_gen
    from app.services.security_scan_service import run_security_scan, register_security_scan

    security_scan_id = str(uuid4_gen())
    register_security_scan(str(scan.id), security_scan_id)
    background_tasks.add_task(run_security_scan, security_scan_id, website.url)

    return ScanResponse.model_validate(scan)


@router.get("/scans/{scan_id}/progress")
async def scan_progress(scan_id: UUID, request: Request):
    event = subscribe(str(scan_id))
    sent = 0

    async def stream():
        nonlocal sent
        try:
            while True:
                if await request.is_disconnected():
                    break

                steps = get_steps(str(scan_id))
                while sent < len(steps):
                    data = json.dumps(steps[sent])
                    yield f"data: {data}\n\n"
                    if steps[sent].get("status") in ("completed", "failed"):
                        return
                    sent += 1

                event.clear()
                try:
                    await asyncio.wait_for(event.wait(), timeout=30.0)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            unsubscribe(str(scan_id), event)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/scans", response_model=list[ScanResponse])
async def list_all_scans(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Scan)
        .join(Website)
        .where(Website.user_id == current_user.id)
        .options(selectinload(Scan.website))
        .order_by(Scan.scan_started_at.desc())
    )
    if status:
        query = query.where(Scan.status == status)

    result = await db.execute(query)
    scans = result.scalars().all()
    return [
        ScanResponse(
            id=s.id,
            website_id=s.website_id,
            status=s.status,
            accessibility_score=s.accessibility_score,
            total_violations=s.total_violations,
            scan_started_at=s.scan_started_at,
            scan_completed_at=s.scan_completed_at,
            scan_mode=s.scan_mode,
            page_results=s.page_results,
            website_name=s.website.name if s.website else None,
            website_url=s.website.url if s.website else None,
        )
        for s in scans
    ]


@router.get("/websites/{website_id}/scans", response_model=list[ScanResponse])
async def list_scans(
    website_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    scans_result = await db.execute(
        select(Scan)
        .where(Scan.website_id == website_id)
        .order_by(Scan.scan_started_at.desc())
    )
    return [ScanResponse.model_validate(s) for s in scans_result.scalars().all()]


@router.get("/scans/{scan_id}/security")
async def get_linked_security_scan(scan_id: UUID):
    from app.services.security_scan_service import get_security_scan_id, get_results

    sec_id = get_security_scan_id(str(scan_id))
    if not sec_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No security scan linked")
    results = get_results(sec_id)
    return {
        "security_scan_id": sec_id,
        "status": results.get("status", "pending") if results else "running",
    }


@router.delete("/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan)
        .join(Website)
        .where(Scan.id == scan_id, Website.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    await db.delete(scan)
    await db.commit()


@router.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan)
        .join(Website)
        .where(Scan.id == scan_id, Website.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return ScanResponse.model_validate(scan)
