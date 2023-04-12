from app.dependencies import logger
from app.infrastructure.clients.redis import RedisClient
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient


async def get_reddis_client() -> IUniqueSetClient:
    """Instantiate and return Redis client."""

    return RedisClient(
        logger=logger,
    )
