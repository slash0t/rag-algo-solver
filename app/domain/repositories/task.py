import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models import Task


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task: ...

    @abstractmethod
    async def get(self, task_id: uuid.UUID) -> Task | None: ...

    @abstractmethod
    async def update(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task_id: uuid.UUID) -> bool: ...
