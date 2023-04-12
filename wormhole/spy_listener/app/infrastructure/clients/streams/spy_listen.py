import asyncio
import base64
import json
from asyncio import AbstractEventLoop
from typing import List

import grpc

from app.dependencies import logger
from app.infrastructure.clients.streams.grpc.spy.v1 import spy_pb2, spy_pb2_grpc
from app.settings import settings
from app.usecases.interfaces.clients.grpc.spy_listen import IStreamClient
from app.usecases.interfaces.services.vaa_manager import IVaaManager


class StreamClient(IStreamClient):
    def __init__(self, vaa_manager: IVaaManager):
        self.vaa_manager = vaa_manager

    async def start(self, loop: AbstractEventLoop) -> None:
        """Starts GRPC connection."""
        loop.create_task(self.connect())

    async def connect(self) -> None:
        channel_options = [
            ("grpc.keepalive_time_ms", 3000000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.keepalive_permit_without_calls", 1),
        ]

        while True:
            try:
                async with grpc.aio.insecure_channel(
                    target=settings.guardian_spy_url, options=channel_options
                ) as channel:
                    logger.info("[StreamClient]: Connected to stream.")
                    stub = spy_pb2_grpc.SpyRPCServiceStub(channel)

                    request = spy_pb2.SubscribeSignedVAARequest(
                        filters=self.__get_filters()
                    )

                    async for response in stub.SubscribeSignedVAA(request):
                        await self.vaa_manager.process(vaa=response.vaa_bytes)

            except grpc.aio.AioRpcError as e:
                logger.error(
                    "[StreamClient]: connection dropped.\nError: %s\n\nAttempting to reconnect...",
                    str(e),
                )
                await asyncio.sleep(settings.reconnect_wait_time)

    def __get_filters(self) -> List[spy_pb2.FilterEntry]:
        filter_list = json.loads(
            base64.b64decode(settings.spy_service_filters).decode("utf-8")
        )
        filters = []

        for vaa_filter in filter_list:
            # Create a filter
            filter_entry = spy_pb2.FilterEntry(emitter_filter=vaa_filter)
            filters.append(filter_entry)

        return filters
