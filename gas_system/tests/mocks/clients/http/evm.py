from enum import Enum

from hexbytes import HexBytes

from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.schemas.blockchain import BlockchainClientError, TransactionHash
from tests import constants as constant


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockEvmClient(IBlockchainClient):
    def __init__(self, result: EvmResult) -> None:
        self.result = result

    async def update(self, data: bytes, remote_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result == EvmResult.SUCCESS:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise BlockchainClientError(detail=constant.EVM_CLIENT_ERROR_DETAIL)
