from enum import Enum
from typing import Optional

from hexbytes import HexBytes
from pydantic import BaseModel


class Ecosystem(str, Enum):
    EVM = "EVM"
    SOLANA = "SOLANA"
    APTOS = "APTOS"


class Chains(int, Enum):
    ETHEREUM = 1
    BSC = 56
    POLYGON = 137
    AVALANCHE = 43114
    FANTOM = 250
    ARBITRUM = 42161
    CELO = 42220


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
    native_value_usd: Optional[float]
