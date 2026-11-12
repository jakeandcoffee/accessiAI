from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteResponse, WebsiteUpdate

router = APIRouter(prefix="/websites", tags=["Websites"])


def _to_response(website: Website) -> WebsiteResponse:
    latest_score = None
    last_scanned = None
    if website.scans:
        latest = website.scans[0]
        latest_score = latest.accessibility_score
        last_scanned = latest.scan_completed_at or latest.scan_started_at
    return WebsiteResponse(
        id=website.id,
        name=website.name,
        url=website.url,
        created_at=website.created_at,
        latest_score=latest_score,
        last_scanned=last_scanned,
    )


@router.get("", response_model=list[WebsiteResponse])
async def list_websites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website)
        .where(Website.user_id == current_user.id)
        .options(selectinload(Website.scans))
        .order_by(Website.created_at.desc())
    )
    return [_to_response(w) for w in result.scalars().all()]


@router.post("", response_model=WebsiteResponse, status_code=status.HTTP_201_CREATED)
async def create_website(
    data: WebsiteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    website = Website(user_id=current_user.id, name=data.name, url=str(data.url))
    db.add(website)
    await db.flush()
    return WebsiteResponse(
        id=website.id, name=website.name, url=website.url, created_at=website.created_at
    )


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website)
        .where(Website.id == website_id, Website.user_id == current_user.id)
        .options(selectinload(Website.scans))
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")
    return _to_response(website)


@router.put("/{website_id}", response_model=WebsiteResponse)
async def update_website(
    website_id: UUID,
    data: WebsiteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    if data.name is not None:
        website.name = data.name
    if data.url is not None:
        website.url = str(data.url)

    await db.flush()
    return WebsiteResponse(
        id=website.id, name=website.name, url=website.url, created_at=website.created_at
    )


@router.delete("/{website_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website(
    website_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    await db.delete(website)
