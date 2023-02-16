from fastapi import APIRouter, Depends, Path, WebSocket
from pydantic import constr

from app.dependencies import get_websocket_client
from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient

transactions_router = APIRouter(tags=["Transactions"])


@transactions_router.websocket("/ws/{address}")
async def websocket_endpoint(
    websocket: WebSocket,
    address: constr(max_length=42, min_length=42) = Path(...),
    websocket_client: IWebsocketClient = Depends(get_websocket_client),
) -> None:
    await websocket_client.open_connection(address=address, connection=websocket)
