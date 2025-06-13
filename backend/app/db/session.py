from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

# DATABASE_URL expected in form: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://music_sync_user:music_sync_password@localhost:5432/music_sync_hub",
)

# Ensure the URL uses the asyncpg driver
if DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Configure session factory
AsyncSessionFactory = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an ``AsyncSession`` and ensures proper close."""

    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close() 