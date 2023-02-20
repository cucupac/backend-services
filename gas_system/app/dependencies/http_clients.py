import base64
import json

from app.dependencies import logger
from app.infrastructure.clients.http.evm import EvmClient
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.fees import Chains, MinimumFees


async def get_evm_client() -> IBlockchainClient:
    """Instantiate and return EVM client."""

    mock_set_send_fees_params = MinimumFees(remote_chain_ids=[], fees=[])

    for chain in Chains:
        mock_set_send_fees_params.remote_chain_ids.append(chain.value)
        mock_set_send_fees_params.fees.append(settings.mock_fee)

    return EvmClient(
        abi=json.loads(base64.b64decode(settings.wormhole_bridge_abi)),
        chain_lookup=json.loads(
            base64.b64decode(settings.chain_lookup).decode("utf-8")
        ),
        mock_set_send_fees_params=mock_set_send_fees_params,
        logger=logger,
    )
