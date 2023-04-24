from app.dependencies import get_event_loop, get_vaa_delivery, logger
from app.infrastructure.clients.redis import RedisClient
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient


async def get_redis_client() -> IUniqueSetClient:
    """Instantiate and return RedisClient."""

    vaa_delivery_service = await get_vaa_delivery()
    loop = await get_event_loop()

    return RedisClient(vaa_delivery=vaa_delivery_service, logger=logger, loop=loop)
