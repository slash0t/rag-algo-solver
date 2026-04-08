import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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

    async def get(self, query_id: uuid.UUID) -> Query:
        async with self._session_factory() as session:
            stmt = select(Query).where(Query.id == query_id)
            result = await session.execute(stmt)
            query = result.scalar_one()
            return query

    async def update(self, query: Query) -> None:
        async with self._session_factory() as session:
            await session.merge(query)
            await session.commit()
