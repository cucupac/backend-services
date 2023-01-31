import databases

from app.dependencies import get_logger
from app.settings import settings

DATABASE = None


async def get_or_create_database():
    global DATABASE
    if DATABASE is not None:
        return DATABASE
    DATABASE = databases.Database(settings.db_url, min_size=5)
    await DATABASE.connect()
    logger = await get_logger()
    logger.info(message="[Database]: Connected to database!")
    return DATABASE
