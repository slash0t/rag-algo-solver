import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.domain.repositories.query import QueryRepository
from app.infrastructure.database.models import Query


class SQLQueryRepository(QueryRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, query: Query) -> Query:
        async with self._session_factory() as session:
            session.add(query)
            await session.commit()
            await session.refresh(query)
            return query

    async def get(self, query_id: uuid.UUID) -> Query | None:
        async with self._session_factory() as session:
            stmt = select(Query).where(Query.id == query_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update(self, query: Query) -> None:
        async with self._session_factory() as session:
            await session.merge(query)
            await session.commit()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        offset: int,
        limit: int,
    ) -> tuple[list[Query], int]:
        async with self._session_factory() as session:
            count_stmt = (
                select(func.count()).select_from(Query).where(Query.user_id == user_id)
            )
            total = (await session.execute(count_stmt)).scalar_one()

            stmt = (
                select(Query)
                .where(Query.user_id == user_id)
                .order_by(Query.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all()), total

    async def get_with_similar_tasks(self, query_id: uuid.UUID) -> Query | None:
        async with self._session_factory() as session:
            stmt = (
                select(Query)
                .options(selectinload(Query.similar_tasks))
                .where(Query.id == query_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
