from app.dependencies import logger
from app.infrastructure.clients.websocket import WebsocketClient
from app.usecases.interfaces.clients.websocket import IWebsocketClient


async def get_websocket_client() -> IWebsocketClient:
    """Instantiate and return WebsocketClient."""
    return WebsocketClient(logger=logger)
