import pytest

from app.usecases.interfaces.repos.tasks import ITasksRepo
from app.usecases.interfaces.tasks.manage_locks import IManageLocksTask


@pytest.mark.asyncio
async def test_task(
    manage_locks_task: IManageLocksTask,
    tasks_repo: ITasksRepo,
    stale_locks: None,  # pylint: disable = unused-argument
) -> None:
    """Test that stale locks are indeed removed."""

    tasks = await tasks_repo.retrieve_all()
    locks = await tasks_repo.retrieve_all_locks()

    assert len(locks) == len(tasks)

    await manage_locks_task.task()

    locks = await tasks_repo.retrieve_all_locks()

    assert len(locks) == 0
