import pytest
from databases import Database

from app.infrastructure.db.core import get_database, get_or_create_database
from app.settings import settings


@pytest.mark.asyncio
async def test_get_or_create_database(test_db_url: str) -> None:
    database = await get_database()
    assert database is None

    settings.db_url = test_db_url

    db = await get_or_create_database()

    database = await get_database()

    assert isinstance(database, Database)
    assert database == db
    assert isinstance(db, Database)
