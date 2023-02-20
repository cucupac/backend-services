from hexbytes import HexBytes
from pydantic import BaseModel


class TransactionHash(HexBytes):
    """Blockchain transaction hash."""


class BlockchainClientException(Exception):
    """Errors raised when interacting with Blockchain nodes."""

    detail: str


class BlockchainClientError(BlockchainClientException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.detail = kwargs.get("detail")


class ComputeCosts(BaseModel):
    gas_price: int
    gas_units: int
