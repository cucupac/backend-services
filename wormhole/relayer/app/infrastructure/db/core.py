from typing import Optional

from databases import Database

from app.dependencies import logger
from app.settings import settings

DATABASE = None


async def get_or_create_database() -> Database:
    print("WE GOT HERE")
    global DATABASE  # pylint: disable=global-statement
    if DATABASE is not None:
        return DATABASE
    DATABASE = Database(settings.db_url, min_size=5)
    await DATABASE.connect()
    logger.info("[Database]: Established connection.")
    return DATABASE


async def get_database() -> Optional[Database]:
    return DATABASE
