from __future__ import annotations

import datetime as _dt

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserPlatformAccount(TimestampMixin, Base):
    """Stores OAuth tokens per streaming service for a user."""

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String, nullable=True)
    expires_at: Mapped[_dt.datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationship
    user: Mapped["User"] = relationship(back_populates="platform_accounts") 