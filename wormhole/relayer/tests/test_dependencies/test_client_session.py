import pytest
from aiohttp import ClientSession

from app.dependencies import get_client_session


@pytest.mark.asyncio
async def test_get_client_session() -> None:

    client_session = await get_client_session()

    assert isinstance(client_session, ClientSession)
