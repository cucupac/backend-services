from app.dependencies import get_event_loop, logger
from app.infrastructure.clients.redis import RedisClient
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient


async def get_reddis_client() -> IUniqueSetClient:
    """Instantiate and return Redis client."""

    return RedisClient(logger=logger, loop=await get_event_loop())
