from databases import Database

from app.dependencies import get_logger
from app.settings import settings

DATABASE = None


async def get_or_create_database() -> Database:
    global DATABASE
    if DATABASE is not None:
        return DATABASE
    DATABASE = Database(settings.db_url, min_size=5)
    await DATABASE.connect()
    logger = get_logger()
    logger.info(message="[Database]: Established connection.")
    return DATABASE
