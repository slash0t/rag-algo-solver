from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings.postgres import PostgresConfig


def create_async_session_factory(config: PostgresConfig) -> async_sessionmaker[AsyncSession]:
    url = f"postgresql+asyncpg://{config.user}:{config.password}@{config.host}:{config.port}/{config.name}"
    engine = create_async_engine(url)
    return async_sessionmaker(engine, expire_on_commit=False)
