from app.dependencies import get_vaa_manager
from app.infrastructure.clients.streams.spy_listen import StreamClient
from app.usecases.interfaces.clients.grpc.spy_listen import IStreamClient

# async def get_stream_client() -> IStreamClient:
#     """Instantiate and return Stream client."""

#     vaa_manager = await get_vaa_manager()

#     return StreamClient(vaa_manager=vaa_manager)


async def get_stream_client() -> IStreamClient:
    """Instantiate and return Stream client."""

    vaa_manager = await get_vaa_manager()

    return StreamClient(vaa_manager=vaa_manager)
