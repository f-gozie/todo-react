from __future__ import annotations

from typing import Generic, TypeVar, Type, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDRepository(Generic[ModelType]):
    """Simple generic repository offering common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, session: AsyncSession, *, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(self, session: AsyncSession, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)  # type: ignore[arg-type]
        session.add(obj)
        await session.flush()
        return obj

    async def update(self, session: AsyncSession, obj_id: int, obj_in: dict) -> ModelType | None:
        stmt = (
            update(self.model).where(self.model.id == obj_id).values(**obj_in).returning(self.model)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.scalar_one_or_none()

    async def delete(self, session: AsyncSession, obj_id: int) -> None:
        await session.execute(delete(self.model).where(self.model.id == obj_id))
        await session.flush() 