from __future__ import annotations

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserPreference(TimestampMixin, Base):
    """Key-value preference storage per user."""

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    preference_key: Mapped[str] = mapped_column(String(100), nullable=False)
    preference_value: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="preferences") 