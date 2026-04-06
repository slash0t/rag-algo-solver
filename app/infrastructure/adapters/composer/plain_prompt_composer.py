from app.domain.models.query import PreparedQuery
from app.domain.services.prompt_composer import PromptComposer


class PlainPromptComposer(PromptComposer):
    async def compose(
        self,
        original_text: str,
        enriched_text: str,
        task_context: str,
    ) -> PreparedQuery:
        text = (
            "Реши алгоритмическую задачу и напиши объяснение для этой задачи "
            "с целью хорошо ее объяснить. "
            f"Задача: {enriched_text}. "
            f"Используя контекст: {task_context}."
        )
        return PreparedQuery(text=text)
