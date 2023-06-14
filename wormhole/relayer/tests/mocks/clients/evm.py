from enum import Enum
from typing import Optional

from hexbytes import HexBytes
from web3.types import Nonce, TxReceipt

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

    async def deliver(
        self, payload: str, nonce: Optional[int] = None
    ) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        if self.result == EvmResult.SUCCESS:
            return HexBytes(constant.TEST_TRANSACTION_HASH)
        raise BlockchainClientError(detail=constant.BLOCKCHAIN_CLIENT_ERROR_DETAIL)

    async def fetch_receipt(self, transaction_hash: str) -> TxReceipt:
        """Fetches the transaction receipt for a given transaction hash."""

        if self.result == EvmResult.SUCCESS:
            return TransactionReceipt(status=1)
        elif self.result == EvmResult.FAILURE:
            return TransactionReceipt(status=0)
        raise BlockchainClientError(detail=BlockchainErrors.TX_HASH_NOT_IN_CHAIN)

    async def get_current_nonce(self) -> Nonce:
        """Retrieves the current nonce of the relayer on a provided destination chain."""
        return Nonce(1)
