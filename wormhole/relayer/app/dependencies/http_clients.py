import base64
import json
from typing import Mapping

from app.dependencies import CHAIN_DATA, WORMHOLE_BRIDGE_ABI, logger
from app.infrastructure.clients.http.evm import EvmClient
from app.settings import settings
from app.usecases.interfaces.clients.http.evm import IEvmClient


async def get_evm_client() -> IEvmClient:
    """Instantiate and return EVM client."""

    return EvmClient(
        abi=WORMHOLE_BRIDGE_ABI,
        chain_data=CHAIN_DATA,
        logger=logger,
    )
