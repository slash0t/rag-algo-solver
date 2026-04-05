from abc import ABC, abstractmethod

from app.domain.models.query import PreparedQuery


class PromptComposer(ABC):
    @abstractmethod
    async def compose(
        self,
        original_text: str,
        enriched_text: str,
        task_context: str,
    ) -> PreparedQuery: ...
