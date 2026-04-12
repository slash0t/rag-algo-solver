import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models import Query


class QueryRepository(ABC):
    @abstractmethod
    async def create(self, query: Query) -> Query: ...

    @abstractmethod
    async def get(self, query_id: uuid.UUID) -> Query | None: ...

    @abstractmethod
    async def update(self, query: Query) -> None: ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: uuid.UUID,
        offset: int,
        limit: int,
    ) -> tuple[list[Query], int]: ...

    @abstractmethod
    async def get_with_similar_tasks(self, query_id: uuid.UUID) -> Query | None: ...
