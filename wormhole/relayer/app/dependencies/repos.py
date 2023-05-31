from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.relays import RelaysRepo
from app.infrastructure.db.repos.tasks import TasksRepo
from app.usecases.interfaces.repos.relays import IRelaysRepo
from app.usecases.interfaces.repos.tasks import ITasksRepo


async def get_relays_repo() -> IRelaysRepo:
    return RelaysRepo(db=await get_or_create_database())


async def get_tasks_repo() -> ITasksRepo:
    return TasksRepo(db=await get_or_create_database())
