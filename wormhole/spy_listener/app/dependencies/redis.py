from app.dependencies import get_event_loop, get_relays_repo, logger
from app.infrastructure.clients.redis import RedisClient
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient

redis_client = None


async def get_redis_client() -> IUniqueSetClient:
    """Instantiate and return Redis client."""
    global redis_client  # pylint: disable = global-statement

    if redis_client is None:
        relays_repo = await get_relays_repo()
        redis_client = RedisClient(
            logger=logger, loop=await get_event_loop(), relays_repo=relays_repo
        )

    return redis_client
