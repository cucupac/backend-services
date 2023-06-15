import math
from typing import Mapping
from datetime import datetime

from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.interfaces.repos.fee_updates import IFeeUpdateRepo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import BlockchainClientError, ComputeCosts, Chains
from app.usecases.schemas.fees import FeeUpdate, MinimumFees
from app.settings import settings


class RemotePriceManager(IRemotePriceManager):
    def __init__(
        self,
        price_client: IPriceClient,
        blockchain_clients: Mapping[int, IBlockchainClient],
        fee_update_repo: IFeeUpdateRepo,
    ):
        self.price_client = price_client
        self.blockchain_clients = blockchain_clients
        self.fee_update_repo = fee_update_repo

    # pylint: disable = too-many-locals
    async def update_remote_fees(self) -> None:
        """Updates gas prices for remote computation in local native token."""

        price_data = await self.price_client.fetch_usd_prices()

        # Estimate fees for each chain
        compute_costs: Mapping[int, ComputeCosts] = {}
        for local_chain_id, data in CHAIN_DATA.items():
            blockchain_client = self.blockchain_clients[local_chain_id]
            costs = await blockchain_client.estimate_fees()

            costs.native_value_usd = price_data[data["native"]]

            compute_costs[local_chain_id] = costs

        # Construct fee information
        fee_updates: Mapping[int, Mapping[int, int]] = {}
        for local_chain_id in CHAIN_DATA:
            local_compute_costs = compute_costs.get(local_chain_id)
            remote_fee_updates: Mapping[int, int] = {}
            for remote_chain_id in CHAIN_DATA:
                if remote_chain_id != local_chain_id:
                    remote_compute_costs = compute_costs.get(remote_chain_id)
                    remote_fee_usd = (
                        remote_compute_costs.gas_units
                        * remote_compute_costs.gas_price
                        * remote_compute_costs.native_value_usd
                    )
                    remote_fee_in_local_native = (
                        remote_fee_usd / local_compute_costs.native_value_usd
                    )

                    # Add buffer
                    remote_fee_in_local_native = await self.add_buffer(
                        remote_chain_id=remote_chain_id,
                        remote_fee_in_local_native=remote_fee_in_local_native,
                    )

                    remote_fee_updates[remote_chain_id] = math.ceil(
                        remote_fee_in_local_native
                    )

            fee_updates[local_chain_id] = remote_fee_updates

        for chain_id, remote_fee_updates in fee_updates.items():
            blockchain_client = self.blockchain_clients[chain_id]
            try:
                transaction_hash_bytes = await blockchain_client.update_fees(
                    remote_data=MinimumFees(
                        remote_chain_ids=list(remote_fee_updates.keys()),
                        remote_fees=list(remote_fee_updates.values()),
                    ),
                )
            except BlockchainClientError as e:
                transaction_hash = None
                error = e.detail
            else:
                transaction_hash = transaction_hash_bytes.hex()
                error = None

            # Store fee update in database
            await self.fee_update_repo.create(
                fee_update=FeeUpdate(
                    chain_id=chain_id,
                    updates=remote_fee_updates,
                    transaction_hash=transaction_hash,
                    error=error,
                )
            )

    async def add_buffer(
        self, remote_chain_id: int, remote_fee_in_local_native: int
    ) -> int:
        """Adds buffer to remote fee."""

        if remote_chain_id == Chains.ETHEREUM:
            if datetime.utcnow().hour > 12 and datetime.utcnow().hour < 18:
                return (
                    remote_fee_in_local_native * settings.higher_ethereum_fee_multiplier
                )
            else:
                return (
                    remote_fee_in_local_native * settings.lower_ethereum_fee_multiplier
                )
        else:
            return remote_fee_in_local_native * settings.default_remote_fee_multiplier
