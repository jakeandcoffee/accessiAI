import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class AIAnalysis(UUIDBase):
    __tablename__ = "ai_analyses"

    violation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_fix: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    violation = relationship("Violation", back_populates="ai_analyses")
