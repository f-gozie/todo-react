from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends

from app.db.session import get_db


async def get_db_session() -> AsyncGenerator:
    """Convenience wrapper for FastAPI dependency injection."""

    async for session in get_db():
        yield session 