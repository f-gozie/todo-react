from __future__ import annotations

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    """Represents an application user that can own playlists and run syncs."""

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    platform_accounts: Mapped[list["UserPlatformAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    playlists: Mapped[list["Playlist"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    sync_history: Mapped[list["SyncHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped[list["UserPreference"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    ) 