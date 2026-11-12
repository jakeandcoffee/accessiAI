import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class Violation(UUIDBase):
    __tablename__ = "violations"

    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="accessibility", nullable=False)
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    impact: Mapped[str] = mapped_column(String(20), nullable=False)
    wcag_criteria: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    help_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    scan = relationship("Scan", back_populates="violations")
    affected_elements = relationship("AffectedElement", back_populates="violation", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="violation", cascade="all, delete-orphan")
    comments = relationship("IssueComment", back_populates="violation", cascade="all, delete-orphan")
