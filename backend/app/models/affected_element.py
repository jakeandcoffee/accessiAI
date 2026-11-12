import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class AffectedElement(UUIDBase):
    __tablename__ = "affected_elements"

    violation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    selector: Mapped[str] = mapped_column(String(1000), nullable=False)
    html: Mapped[str] = mapped_column(Text, nullable=False)
    failure_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    violation = relationship("Violation", back_populates="affected_elements")
