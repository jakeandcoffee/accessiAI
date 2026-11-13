import os
import shutil
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteResponse, WebsiteUpdate

UPLOAD_DIR = "/app/uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

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
        page_urls=website.page_urls or [],
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
    website = Website(
        user_id=current_user.id,
        name=data.name,
        url=str(data.url),
        page_urls=[str(u) for u in data.page_urls],
    )
    db.add(website)
    await db.flush()
    return WebsiteResponse(
        id=website.id,
        name=website.name,
        url=website.url,
        page_urls=website.page_urls or [],
        created_at=website.created_at,
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
    if data.page_urls is not None:
        website.page_urls = [str(u) for u in data.page_urls]

    await db.flush()
    return WebsiteResponse(
        id=website.id,
        name=website.name,
        url=website.url,
        page_urls=website.page_urls or [],
        created_at=website.created_at,
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


@router.post("/{website_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    website_id: UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 20MB)")

    attachment_id = str(uuid4())
    dest_dir = os.path.join(UPLOAD_DIR, str(website_id))
    os.makedirs(dest_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1]
    stored_name = f"{attachment_id}{ext}"
    dest_path = os.path.join(dest_dir, stored_name)
    with open(dest_path, "wb") as f:
        f.write(contents)

    attachment_meta = {
        "id": attachment_id,
        "filename": file.filename or "unknown",
        "stored_name": stored_name,
        "size": len(contents),
        "content_type": file.content_type or "application/octet-stream",
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    attachments = list(website.attachments or [])
    attachments.append(attachment_meta)
    website.attachments = attachments
    await db.flush()

    return attachment_meta


@router.get("/{website_id}/attachments/{attachment_id}")
async def download_attachment(
    website_id: UUID,
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    attachment = next((a for a in (website.attachments or []) if a["id"] == attachment_id), None)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    file_path = os.path.join(UPLOAD_DIR, str(website_id), attachment["stored_name"])
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing from storage")

    return FileResponse(
        file_path,
        filename=attachment["filename"],
        media_type=attachment.get("content_type", "application/octet-stream"),
    )


@router.delete("/{website_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    website_id: UUID,
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Website).where(Website.id == website_id, Website.user_id == current_user.id)
    )
    website = result.scalar_one_or_none()
    if not website:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Website not found")

    attachments = list(website.attachments or [])
    attachment = next((a for a in attachments if a["id"] == attachment_id), None)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    file_path = os.path.join(UPLOAD_DIR, str(website_id), attachment["stored_name"])
    if os.path.isfile(file_path):
        os.remove(file_path)

    website.attachments = [a for a in attachments if a["id"] != attachment_id]
    await db.flush()
