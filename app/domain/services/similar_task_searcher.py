from abc import ABC, abstractmethod

from app.domain.models.query import SimilarTask


class SimilarTaskSearcher(ABC):
    @abstractmethod
    async def search(self, query_text: str) -> list[SimilarTask]: ...
