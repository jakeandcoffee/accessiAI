import uuid

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class Website(UUIDBase):
    __tablename__ = "websites"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    page_urls: Mapped[list[str]] = mapped_column(JSON, default=list, server_default="[]", nullable=False)
    attachments: Mapped[list[dict]] = mapped_column(JSON, default=list, server_default="[]", nullable=False)

    owner = relationship("User", back_populates="websites")
    scans = relationship("Scan", back_populates="website", cascade="all, delete-orphan", order_by="Scan.scan_started_at.desc()")

    @property
    def scan_urls(self) -> list[str]:
        """Primary URL followed by every additional page, de-duplicated in order."""
        urls: list[str] = []
        for u in [self.url, *(self.page_urls or [])]:
            if u and u not in urls:
                urls.append(u)
        return urls
