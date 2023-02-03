from typing import Optional

from aiohttp import ClientSession

client_session: Optional[ClientSession] = None


async def get_client_session() -> ClientSession:
    global client_session  # pylint: disable = global-statement
    if client_session is None:
        client_session = ClientSession()
    return client_session
