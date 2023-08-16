from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.tasks import TaskInDb, TaskLockInDb


class ITasksRepo(ABC):
    @abstractmethod
    async def create_lock(self, task_id: id) -> Optional[int]:
        """Attempt to create a lock for a given task."""

    @abstractmethod
    async def retrieve_all(self) -> List[TaskInDb]:
        """Retrives all tasks."""

    @abstractmethod
    async def retrieve(self, task_name: str) -> TaskInDb:
        """Retrieves task by name."""

    @abstractmethod
    async def retrieve_all_locks(self) -> List[TaskLockInDb]:
        """Retrives all task locks."""

    @abstractmethod
    async def delete_lock(self, task_id: int) -> None:
        """Deletes a task lock by task_id."""
