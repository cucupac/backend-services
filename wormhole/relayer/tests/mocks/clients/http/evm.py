from enum import Enum

from hexbytes import HexBytes

from app.usecases.interfaces.clients.http.evm import IEvmClient
from app.usecases.schemas.evm import EvmClientError, TransactionHash
from tests import constants as constant


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MockEvmClient(IEvmClient):
    def __init__(self, result: EvmResult) -> None:
        self.result = result

    async def deliver(self, vaa: bytes, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result == EvmResult.SUCCESS:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise EvmClientError(detail=constant.EVM_CLIENT_ERROR_DETAIL)
