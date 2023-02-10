from fastapi import Depends

from app.dependencies import get_logger
from app.infrastructure.clients.ws.websocket import WebsocketClient
from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient
from app.usecases.interfaces.dependencies.logger import ILogger


async def get_websocket_client(
    logger: ILogger = Depends(get_logger),
) -> IWebsocketClient:
    """Instantiate and return WebsocketClient client."""
    websocket_client = WebsocketClient(logger=logger)
    return websocket_client
