from logging import Logger
from typing import Mapping, Optional

from fastapi import WebSocket, WebSocketDisconnect

from app.usecases.interfaces.clients.ws.websocket import IWebsocketClient
from app.usecases.schemas.relays import Status


class WebsocketClient(IWebsocketClient):

    _instance: IWebsocketClient = None

    def __new__(cls, logger: Logger) -> IWebsocketClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger: Logger = logger
            cls._instance.clients: Mapping[str, WebSocket] = {}
        return cls._instance

    async def open_connection(self, address: str, connection: WebSocket) -> None:
        """Open websocket connection and store it in dictionary."""
        await connection.accept()

        self.clients[address] = connection

        try:
            while True:
                await connection.receive_text()
        except WebSocketDisconnect as e:
            self.logger.info("[WebsocketClient]: Disconnect: %s.", e)
            address = connection.scope.get("path").split("/")[-1]
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
