from __future__ import annotations

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SyncHistory(TimestampMixin, Base):
    """Represents an instance of a sync run triggered by a user."""

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    sync_type: Mapped[str] = mapped_column(String(50), nullable=False)  # playlists, liked_songs, etc.
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # pending, success, failed

    started_at: Mapped[float | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[float | None] = mapped_column(DateTime(timezone=True))

    details: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="sync_history") 