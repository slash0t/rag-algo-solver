import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repositories.query_processing import QueryProcessingRepository
from app.infrastructure.database.models import QueryProcessing


class SQLQueryProcessingRepository(QueryProcessingRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, processing: QueryProcessing) -> QueryProcessing:
        async with self._session_factory() as session:
            session.add(processing)
            await session.commit()
            await session.refresh(processing)
            return processing

    async def get(self, processing_id: uuid.UUID) -> QueryProcessing:
        async with self._session_factory() as session:
            stmt = select(QueryProcessing).where(QueryProcessing.id == processing_id)
            result = await session.execute(stmt)
            processing = result.scalar_one()
            return processing

    async def update(self, processing: QueryProcessing) -> None:
        async with self._session_factory() as session:
            await session.merge(processing)
            await session.commit()
