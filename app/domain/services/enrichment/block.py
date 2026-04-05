from abc import ABC, abstractmethod

from app.domain.models.query import IntermediateQuery


class EnrichmentBlock(ABC):
    @abstractmethod
    async def process(self, query: IntermediateQuery) -> IntermediateQuery: ...
