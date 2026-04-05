from abc import ABC, abstractmethod

from app.domain.models.query import SimilarTask


class TaskContextBuilder(ABC):
    @abstractmethod
    async def build(self, tasks: list[SimilarTask]) -> str: ...
