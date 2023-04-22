from app.dependencies import get_event_loop, logger
from app.infrastructure.clients.redis import RedisClient
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient

redis_client = None


async def get_reddis_client() -> IUniqueSetClient:
    """Instantiate and return Redis client."""
    global redis_client  # pylint: disable = global-statement

    if redis_client is None:
        redis_client = RedisClient(logger=logger, loop=await get_event_loop())

    return redis_client
