from app.dependencies import CHAIN_DATA, logger
from app.infrastructure.clients.evm import EvmClient
from app.usecases.interfaces.clients.evm import IEvmClient


async def get_evm_client(ax_chain_id: int) -> IEvmClient:
    """Instantiate and return an EVM client."""

    return EvmClient(
        chain_id=ax_chain_id,
        rpc_url=CHAIN_DATA[ax_chain_id]["rpc"],
        logger=logger,
    )
