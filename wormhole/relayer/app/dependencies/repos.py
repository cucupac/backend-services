from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.relays import RelaysRepo
from app.usecases.interfaces.repos.relays import IRelaysRepo


async def get_relays_repo() -> IRelaysRepo:
    return RelaysRepo(db=await get_or_create_database())
