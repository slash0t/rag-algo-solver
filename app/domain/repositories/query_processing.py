import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models import QueryProcessing


class QueryProcessingRepository(ABC):
    @abstractmethod
    async def create(self, processing: QueryProcessing) -> QueryProcessing: ...

    @abstractmethod
    async def get(self, processing_id: uuid.UUID) -> QueryProcessing: ...

    @abstractmethod
    async def update(self, processing: QueryProcessing) -> None: ...
