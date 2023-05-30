from enum import Enum

from hexbytes import HexBytes

from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.blockchain import (
    BlockchainClientError,
    BlockchainErrors,
    TransactionHash,
    TransactionReceipt,
)
from tests import constants as constant


class EvmResult(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ERROR = "ERROR"


class MockEvmClient(IEvmClient):
    def __init__(self, result: EvmResult) -> None:
        self.result = result

    async def deliver(self, payload: bytes, dest_chain_id: int) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result == EvmResult.SUCCESS:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise BlockchainClientError(detail=constant.BLOCKCHAIN_CLIENT_ERROR_DETAIL)

    async def fetch_receipt(
        self, transaction_hash, dest_chain_id
    ) -> TransactionReceipt:
        """Fetches the transaction receipt for a given transaction hash."""
        if self.result == EvmResult.SUCCESS:
            return TransactionReceipt(status=1)
        elif self.result == EvmResult.FAILURE:
            return TransactionReceipt(status=0)
        raise BlockchainClientError(detail=BlockchainErrors.TX_HASH_NOT_IN_CHAIN)

    async def get_current_nonce(self, dest_chain_id: int) -> int:
        """Retrieves the current nonce of the relayer on a provided destination chain."""
