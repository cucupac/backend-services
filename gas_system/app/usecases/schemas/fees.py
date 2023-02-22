from enum import Enum
from typing import List, Mapping

from pydantic import BaseModel


class Chains(int, Enum):
    ETHEREUM = 1
    BSC = 56
    POLYGON = 137
    AVALANCHE = 43114
    FANTOM = 250
    MOONBEAM = 1284
    ARBITRUM = 42161
    CELO = 42220


class MinimumFees(BaseModel):
    remote_chain_ids: List[Chains]
    remote_fees: List[int]


class FeeUpdate(BaseModel):
    chain_id: int
    updates: Mapping[int, int]
    transaction_hash: str
    error: str
