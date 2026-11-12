from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import UUIDBase


class User(UUIDBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)

    websites = relationship("Website", back_populates="owner", cascade="all, delete-orphan")
    comments = relationship("IssueComment", back_populates="user", cascade="all, delete-orphan")
