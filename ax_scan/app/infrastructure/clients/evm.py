from logging import Logger
from typing import Any, List, Mapping

from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.types import LogReceipt, TxReceipt

from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.blockchain import BlockchainClientError


class EvmClient(IEvmClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_id: int,
        rpc_url: str,
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_id = chain_id
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.logger = logger

    async def fetch_receipt(self, transaction_hash: str) -> TxReceipt:
        """Fetches the transaction receipt for a given transaction hash."""
        try:
            return await self.web3_client.eth.wait_for_transaction_receipt(
                transaction_hash=transaction_hash, timeout=120, poll_latency=0.1
            )
        except Exception as e:
            self.logger.error("[EvmClient]: Tx receipt retrieval failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def fetch_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[LogReceipt]:
        """Fetches events emitted from given contract, for a given block range."""

        event_filter = {
            "address": contract,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [settings.send_to_chain_topic, settings.receive_from_chain_topic],
        }

        return self.web3_client.eth.get_logs(event_filter)
