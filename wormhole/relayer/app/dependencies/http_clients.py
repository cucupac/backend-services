import base64
import json

from app.dependencies import logger
from app.infrastructure.clients.http.evm import EvmClient
from app.settings import settings
from app.usecases.interfaces.clients.http.evm import IEvmClient


async def get_evm_client() -> IEvmClient:
    """Instantiate and return EVM client."""

    return EvmClient(
        abi=json.loads(base64.b64decode(settings.wormhole_bridge_abi)), logger=logger
    )
