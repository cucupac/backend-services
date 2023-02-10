from app.dependencies import logger
from app.infrastructure.clients.ws.websocket import WebsocketClient
from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient


async def get_websocket_client() -> IWebsocketClient:
    """Instantiate and return WebsocketClient client."""
    websocket_client = WebsocketClient(logger=logger)
    return websocket_client
