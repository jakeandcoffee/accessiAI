import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class Scan(UUIDBase):
    __tablename__ = "scans"

    website_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    accessibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_violations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scan_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scan_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    website = relationship("Website", back_populates="scans")
    violations = relationship("Violation", back_populates="scan", cascade="all, delete-orphan")
