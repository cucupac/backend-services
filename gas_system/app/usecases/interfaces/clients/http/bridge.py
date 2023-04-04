from abc import ABC, abstractmethod

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract

from app.usecases.schemas.fees import MinimumFees


class IBridgeClient(ABC):
    @abstractmethod
    async def craft_transaction(
        self,
        remote_data: MinimumFees,
        contract: Contract,
        web3_client: Web3,
        post_london_upgrade: bool,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

    @abstractmethod
    async def estimate_gas_units(
        self, contract: Contract, web3_client: Web3, post_london_upgrade: bool
    ) -> int:
        """Estimates a transaction's gas information."""
