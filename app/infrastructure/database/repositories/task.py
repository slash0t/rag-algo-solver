import uuid

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repositories.task import TaskRepository
from app.infrastructure.database.models import Task


class SQLTaskRepository(TaskRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, task: Task) -> Task:
        async with self._session_factory() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    async def get(self, task_id: uuid.UUID) -> Task | None:
        async with self._session_factory() as session:
            stmt = select(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update(self, task: Task) -> Task:
        async with self._session_factory() as session:
            merged = await session.merge(task)
            await session.commit()
            await session.refresh(merged)
            return merged

    async def delete(self, task_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            stmt = sa_delete(Task).where(Task.id == task_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
