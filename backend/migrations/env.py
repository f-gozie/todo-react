from __future__ import annotations

import asyncio
import logging
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Add project root to path
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import async_engine  # noqa: E402
from app.models import Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config  # type: ignore[attr-defined]

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)  # type: ignore[arg-type]
logger = logging.getLogger("alembic.env")

target_metadata = Base.metadata


def run_migrations_offline() -> None:  # pragma: no cover
    """Run migrations in 'offline' mode."""

    url = async_engine.url
    context.configure(
        url=str(url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:  # pragma: no cover
    """Run migrations in 'online' mode."""

    connectable: AsyncEngine = async_engine

    async def run_async_migrations() -> None:  # type: ignore[has-type]
        async with connectable.connect() as connection:  # type: ignore[call-arg]
            await connection.run_sync(do_run_migrations)

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 