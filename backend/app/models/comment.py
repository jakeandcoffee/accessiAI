import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class IssueComment(UUIDBase):
    __tablename__ = "issue_comments"

    violation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    violation = relationship("Violation", back_populates="comments")
    user = relationship("User", back_populates="comments")
