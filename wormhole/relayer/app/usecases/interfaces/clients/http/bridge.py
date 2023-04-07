from abc import ABC, abstractmethod

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract


class IBridgeClient(ABC):
    @abstractmethod
    async def craft_transaction(
        self,
        payload: bytes,
        contract: Contract,
        web3_client: Web3,
        post_london_upgrade: bool,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""
