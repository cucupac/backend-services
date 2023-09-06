from logging import Logger
from typing import List, Union

from web3 import AsyncHTTPProvider, AsyncWeb3

from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.blockchain import BlockchainClientError, TransactionReceipt
from app.usecases.schemas.events import (
    EmitterAddress,
    Mint,
    ReceiveFromChain,
    SendToChain,
)


class EvmClient(IEvmClient):
    def __init__(
        self,
        chain_id: int,
        rpc_url: str,
        logger: Logger,
    ) -> None:
        self.chain_id = chain_id
        self.web3_client = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.logger = logger

    async def fetch_receipt(self, transaction_hash: str) -> TransactionReceipt:
        """Fetches the transaction receipt for a given transaction hash."""
        try:
            receipt = await self.web3_client.eth.get_transaction_receipt(
                transaction_hash=transaction_hash
            )
        except Exception as e:
            self.logger.error("[EvmClient]: Tx receipt retrieval failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e
        return TransactionReceipt(
            status=receipt.status,
            gas_used=receipt.gasUsed,
            gas_price=receipt.effectiveGasPrice,
        )

    async def fetch_transfer_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Union[SendToChain, ReceiveFromChain]]:
        """Fetches cross-chain transfer events emitted from given contract, for a given block range."""

        event_filter = {
            "address": contract,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [
                [settings.send_to_chain_topic, settings.receive_from_chain_topic]
            ],
        }

        try:
            events_raw = await self.web3_client.eth.get_logs(event_filter)
        except Exception as e:
            self.logger.error(
                "[EvmClient]: Transfer event retrieval failed. Error: %s", e
            )
            raise BlockchainClientError(detail=str(e)) from e
        events = []
        for event in events_raw:
            if event.topics[0].hex() == settings.send_to_chain_topic:
                if contract == EmitterAddress.WORMHOLE_BRIDGE:
                    source_chain_id = CHAIN_DATA[self.chain_id]["wh_chain_id"]
                elif contract == EmitterAddress.LAYER_ZERO_BRIDGE:
                    source_chain_id = CHAIN_DATA[self.chain_id]["lz_chain_id"]
                events.append(
                    SendToChain(
                        emitter_address=event.address,
                        block_number=event.blockNumber,
                        block_hash=event.blockHash.hex(),
                        transaction_hash=event.transactionHash.hex(),
                        source_chain_id=source_chain_id,
                        dest_chain_id=int(event.topics[1].hex(), 16),
                        amount=int(event.data.hex()[2:66], 16),
                        message_id=int(event.data.hex()[66:130], 16),
                        from_address=AsyncWeb3.to_checksum_address(
                            event.topics[2].hex()[2:].lstrip("0")
                        ),
                    )
                )
            else:
                if contract == EmitterAddress.WORMHOLE_BRIDGE:
                    dest_chain_id = CHAIN_DATA[self.chain_id]["wh_chain_id"]
                elif contract == EmitterAddress.LAYER_ZERO_BRIDGE:
                    dest_chain_id = CHAIN_DATA[self.chain_id]["lz_chain_id"]

                events.append(
                    ReceiveFromChain(
                        emitter_address=event.address,
                        block_number=event.blockNumber,
                        block_hash=event.blockHash.hex(),
                        transaction_hash=event.transactionHash.hex(),
                        source_chain_id=int(event.topics[1].hex(), 16),
                        dest_chain_id=dest_chain_id,
                        amount=int(event.data.hex()[2:66], 16),
                        message_id=int(event.data.hex()[66:130], 16),
                        to_address=AsyncWeb3.to_checksum_address(
                            event.topics[3].hex()[2:].lstrip("0")
                        ),
                    )
                )

        return events

    async def fetch_mint_events(
        self, contract: str, from_block: int, to_block: int
    ) -> List[Mint]:
        """Fetches mint events emitted from given contract, for a given block range."""

        event_filter = {
            "address": contract,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [[settings.mint_topic]],
        }

        try:
            events_raw = await self.web3_client.eth.get_logs(event_filter)
        except Exception as e:
            self.logger.error("[EvmClient]: Mint event retrieval failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

        events = []
        for event in events_raw:
            events.append(
                Mint(
                    emitter_address=event.address,
                    block_number=event.blockNumber,
                    block_hash=event.blockHash.hex(),
                    transaction_hash=event.transactionHash.hex(),
                    account=AsyncWeb3.to_checksum_address(
                        event.topics[1].hex()[2:].lstrip("0")
                    ),
                    amount=int(event.data.hex()[2:], 16),
                )
            )
        return events

    async def fetch_latest_block_number(self) -> int:
        """Fetches the latest block number."""

        return await self.web3_client.eth.block_number
