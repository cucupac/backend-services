from logging import Logger
from typing import Any, List, Mapping, Optional

from eth_account.datastructures import SignedTransaction
from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt

from app.dependencies import CHAIN_ID_LOOKUP
from app.settings import settings
from app.usecases.interfaces.clients.evm import IEvmClient
from app.usecases.schemas.blockchain import BlockchainClientError, TransactionHash


class EvmClient(IEvmClient):
    def __init__(
        self,
        abi: List[Mapping[str, Any]],
        chain_data: Mapping[str, str],
        logger: Logger,
    ) -> None:
        self.abi = abi
        self.chain_data = chain_data
        self.logger = logger

    async def deliver(
        self, payload: str, dest_chain_id: int, nonce: Optional[int] = None
    ) -> TransactionHash:
        """Sends transaction to the destination blockchain."""
        web3_client = Web3(
            Web3.HTTPProvider(self.chain_data[CHAIN_ID_LOOKUP[dest_chain_id]]["rpc"])
        )

        contract = web3_client.eth.contract(
            address=web3_client.toChecksumAddress(settings.evm_wormhole_bridge),
            abi=self.abi,
        )

        try:
            signed_transaction = await self.__craft_transaction(
                payload=payload,
                contract=contract,
                web3_client=web3_client,
                chain_data=self.chain_data[CHAIN_ID_LOOKUP[dest_chain_id]],
                nonce=nonce
                if nonce
                else await self.get_current_nonce(dest_chain_id=dest_chain_id),
            )
            return web3_client.eth.send_raw_transaction(
                transaction=signed_transaction.rawTransaction
            )
        except Exception as e:
            self.logger.error("[EvmClient]: VAA delivery failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def fetch_receipt(
        self, transaction_hash: str, dest_chain_id: int
    ) -> TxReceipt:
        """Fetches the transaction receipt for a given transaction hash."""
        web3_client = Web3(
            Web3.HTTPProvider(self.chain_data[CHAIN_ID_LOOKUP[dest_chain_id]]["rpc"])
        )

        try:
            return web3_client.eth.wait_for_transaction_receipt(transaction_hash)
        except Exception as e:
            self.logger.error("[EvmClient]: Tx receipt retrieval failed. Error: %s", e)
            raise BlockchainClientError(detail=str(e)) from e

    async def get_current_nonce(self, dest_chain_id: int) -> int:
        """Retrieves the current nonce of the relayer on a provided destination chain."""

        web3_client = Web3(
            Web3.HTTPProvider(self.chain_data[CHAIN_ID_LOOKUP[dest_chain_id]]["rpc"])
        )

        return web3_client.eth.get_transaction_count(
            web3_client.toChecksumAddress(settings.relayer_address)
        )

    async def __craft_transaction(
        self,
        payload: str,
        contract: Contract,
        web3_client: Web3,
        chain_data: Mapping[str, Any],
        nonce: int,
    ) -> SignedTransaction:
        """Craft a raw transaction to be sent to the blockchain."""

        # Obtain destination chain information
        post_london_upgrade = chain_data["post_london_upgrade"]
        has_fee_history = chain_data["has_fee_history"]

        # Build transaction
        transaction_dict = {
            "from": web3_client.toChecksumAddress(settings.relayer_address),
            "nonce": nonce,
        }

        gas_price_estimate = web3_client.eth.gas_price

        if post_london_upgrade:
            if has_fee_history:
                fee_history = web3_client.eth.fee_history(
                    block_count=1,
                    newest_block="latest",
                    reward_percentiles=[settings.priority_fee_percentile],
                )

                base_fee_per_gas = fee_history.baseFeePerGas[-1]
                max_priority_fee = fee_history.reward[0][0]
            else:
                base_fee_per_gas = gas_price_estimate
                max_priority_fee = web3_client.eth.max_priority_fee

            transaction_dict["maxFeePerGas"] = base_fee_per_gas + max_priority_fee
            transaction_dict["maxPriorityFeePerGas"] = max_priority_fee
        else:
            transaction_dict["gasPrice"] = gas_price_estimate

        transaction = contract.functions.processMessage(payload).build_transaction(
            transaction_dict
        )

        return web3_client.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=settings.relayer_private_key
        )
