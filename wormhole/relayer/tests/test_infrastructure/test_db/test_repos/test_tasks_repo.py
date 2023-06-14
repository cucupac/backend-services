# pylint: disable=unused-argument
import pytest
from databases import Database

from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.schemas.tasks import TaskInDb, TaskLockInDb, TaskName


@pytest.mark.asyncio
async def test_create_lock(
    tasks_repo: ITasksRepo,
) -> None:
    tasks = await tasks_repo.retrieve_all()

    for task in tasks:
        available_task = await tasks_repo.create_lock(task_id=task.id)
        assert available_task
        available_task = await tasks_repo.create_lock(task_id=task.id)
        assert not available_task


@pytest.mark.asyncio
async def test_retrieve(
    tasks_repo: ITasksRepo,
) -> None:
    for name in TaskName:
        task = await tasks_repo.retrieve(task_name=name.value)
        assert task.name == name.value


@pytest.mark.asyncio
async def test_retrieve_all(
    tasks_repo: ITasksRepo,
) -> None:
    tasks = await tasks_repo.retrieve_all()

    assert len(tasks) == len(TaskName)

    for task in tasks:
        assert isinstance(task, TaskInDb)


@pytest.mark.asyncio
async def test_retrieve_all_locks(tasks_repo: ITasksRepo, stale_locks: None) -> None:
    tasks = await tasks_repo.retrieve_all()
    locks = await tasks_repo.retrieve_all_locks()

    assert len(locks) == len(tasks)

    for lock in locks:
        assert isinstance(lock, TaskLockInDb)


@pytest.mark.asyncio
async def test_delete(
    tasks_repo: ITasksRepo, test_db: Database, stale_locks: None
) -> None:
    tasks = await tasks_repo.retrieve_all()
    locks = await tasks_repo.retrieve_all_locks()

    assert len(locks) == len(tasks)

    for lock in locks:
        await tasks_repo.delete_lock(task_id=lock.task_id)

        deleted_lock = await test_db.fetch_one(
            """SELECT * FROM task_locks AS tl WHERE tl.task_id=:task_id""",
            {
                "task_id": lock.task_id,
            },
        )

        assert deleted_lock is None

    locks = await tasks_repo.retrieve_all_locks()

    assert len(locks) == 0
