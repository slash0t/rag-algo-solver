from app.domain.models.query import SimilarTask
from app.domain.services.task_context_builder import TaskContextBuilder


class PlainTaskContextBuilder(TaskContextBuilder):
    async def build(self, tasks: list[SimilarTask]) -> str:
        parts = [
            f"Задача: {task.task_text}. Решение: {task.solution}" for task in tasks
        ]
        return "\n".join(parts)
