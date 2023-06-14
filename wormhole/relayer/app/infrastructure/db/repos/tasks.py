from typing import List, Optional

import asyncpg
from databases import Database

from app.infrastructure.db.models.tasks import TASK_LOCKS, TASKS
from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.schemas.tasks import TaskInDb, TaskLockInDb


class TasksRepo(ITasksRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create_lock(self, task_id: id) -> Optional[int]:
        """Attempt to create a lock for a given task."""

        insert_statement = TASK_LOCKS.insert().values(task_id=task_id)

        try:
            return await self.db.execute(insert_statement)
        except asyncpg.exceptions.UniqueViolationError:
            return None

    async def retrieve(self, task_name: str) -> TaskInDb:
        """Retrieves task by name."""

        query = TASKS.select().where(TASKS.c.name == task_name)

        result = await self.db.fetch_one(query)

        return TaskInDb(**result)

    async def retrieve_all(self) -> List[TaskInDb]:
        """Retrives all tasks."""
        query = TASKS.select()

        results = await self.db.fetch_all(query)

        return [TaskInDb(**result) for result in results]

    async def retrieve_all_locks(self) -> List[TaskLockInDb]:
        """Retrives all task locks."""
        query = TASK_LOCKS.select()

        results = await self.db.fetch_all(query)

        return [TaskLockInDb(**result) for result in results]

    async def delete_lock(self, task_id: int) -> None:
        """Deletes a task lock by task_id."""

        delete_statement = TASK_LOCKS.delete().where(TASK_LOCKS.c.task_id == task_id)

        await self.db.execute(delete_statement)
