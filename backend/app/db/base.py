from __future__ import annotations

import datetime as _dt
from typing import Any

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` columns with automatic updates."""

    created_at: Mapped[_dt.datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[_dt.datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class Base(DeclarativeBase):
    """Project-wide declarative base that all models should inherit from."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # __repr__ helper for easier debugging
    def __repr__(self) -> str:  # pragma: no cover
        attrs: list[str] = [
            f"{col.key}={getattr(self, col.key)!r}" for col in self.__table__.columns
        ]
        return f"<{self.__class__.__name__} {' '.join(attrs)}>"

    # Generate table name automatically (snake_case of class name)
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower() 