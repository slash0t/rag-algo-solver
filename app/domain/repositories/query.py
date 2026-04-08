import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models import Query


class QueryRepository(ABC):
    @abstractmethod
    async def create(self, query: Query) -> Query: ...

    @abstractmethod
    async def get(self, query_id: uuid.UUID) -> Query: ...

    @abstractmethod
    async def update(self, query: Query) -> None: ...
