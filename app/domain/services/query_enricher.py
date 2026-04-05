from abc import ABC, abstractmethod

from app.domain.models.query import RawQuery


class QueryEnricher(ABC):
    @abstractmethod
    async def enrich(self, raw_query: RawQuery) -> str: ...
