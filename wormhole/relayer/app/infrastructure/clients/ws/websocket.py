from typing import Mapping, Optional

from fastapi import WebSocket, WebSocketDisconnect

from app.usecases.interfaces.dependencies.logger import ILogger
from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient
from app.usecases.schemas.relays import Status


class WebsocketClient(IWebsocketClient):
    def __init__(self, logger: ILogger):
        self.clients: Mapping[
            str, WebSocket
        ] = dict()
        self.logger = logger

    async def open_connection(self, address: str, connection: WebSocket) -> None:
        """Open websocket connection and store it in dictionary."""
        await connection.accept()

        try:
            while True:
                data = await connection.receive_text()
        except WebSocketDisconnect as e:
            print(f"\n\nError: {e}\n\n")
        

    async def close_connection(self, address: str) -> None:
        """Close websocket connection."""

        connection = self.clients.get(address)
        # 1. close connection
        await connection.close(reason="Connection closed.")

        # 2. remove from dictionary
        del self.clients[address]

    async def notify_client(
        self,
        address: str,
        status: Status,
        error: Optional[str],
        transaction_hash: Optional[str],
    ) -> None:
        """Notify client that action occured."""

        message = {
            "transaction_hash": transaction_hash,
            "status": status,
            "error": error,
        }

        connection = self.clients.get(address)

        if connection:
            await connection.send_json(data=message)
