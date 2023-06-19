from datetime import datetime
from math import ceil
from statistics import median
from typing import List, Mapping

from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import BlockchainClientError, Chains, ComputeCosts
from app.usecases.schemas.fees import FeeUpdate, FeeUpdateError, MinimumFees, Status


class RemotePriceManager(IRemotePriceManager):
    def __init__(
        self,
        price_client: IPriceClient,
        blockchain_clients: Mapping[int, IBlockchainClient],
        fee_update_repo: IFeeUpdatesRepo,
    ):
        self.price_client = price_client
        self.blockchain_clients = blockchain_clients
        self.fee_update_repo = fee_update_repo
        self.no_update_chains = []

    async def update_remote_fees(self, chains_to_update: List[int]) -> None:
        """Updates gas prices for remote computation in local native token."""

        # Estimate fees for each chain
        chain_compute_costs = await self.get_chain_compute_costs()

        # Check that gas prices are tolerable
        self.no_update_chains = []
        for chain_id in CHAIN_DATA:
            compute_costs = chain_compute_costs[chain_id]
            do_update = await self.check_gas_price(
                chain_id=chain_id, compute_costs=compute_costs
            )

            if not do_update:
                self.no_update_chains.append(chain_id)

        # Construct remote fee information, per chain
        fee_updates = await self.get_remote_fees(
            compute_costs=chain_compute_costs, chains_to_update=chains_to_update
        )

        # Update fees on each source chain
        for chain_id, remote_fee_updates in fee_updates.items():
            if chain_id not in self.no_update_chains:
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
                    status = Status.FAILED
                    error = e.detail
                else:
                    if any(
                        chain_id in self.no_update_chains
                        for chain_id in remote_fee_updates
                    ):
                        status = Status.FAILED
                        error = FeeUpdateError.DESTINATION_PRICE_TOO_HIGH
                    else:
                        status = Status.SUCCESS
                        error = None
                    transaction_hash = transaction_hash_bytes.hex()

                # Store fee update in database
                await self.fee_update_repo.create(
                    fee_update=FeeUpdate(
                        chain_id=chain_id,
                        updates=remote_fee_updates,
                        transaction_hash=transaction_hash,
                        status=status,
                        error=error,
                    )
                )
            else:
                await self.fee_update_repo.create(
                    fee_update=FeeUpdate(
                        chain_id=chain_id,
                        updates=remote_fee_updates,
                        transaction_hash=None,
                        status=Status.FAILED,
                        error=FeeUpdateError.TX_FEE_TOO_HIGH,
                    )
                )

    async def add_buffer(
        self, remote_chain_id: int, remote_fee_in_local_native: int
    ) -> int:
        """Adds buffer to remote fee."""

        if remote_chain_id == Chains.ETHEREUM:
            if datetime.utcnow().hour >= 12 and datetime.utcnow().hour < 18:
                return (
                    remote_fee_in_local_native * settings.higher_ethereum_fee_multiplier
                )
            return remote_fee_in_local_native * settings.lower_ethereum_fee_multiplier
        return remote_fee_in_local_native * settings.remote_fee_multiplier

    async def get_chain_compute_costs(self) -> Mapping[int, ComputeCosts]:
        """Returns the cost of delivery data on all chains."""

        price_data = await self.price_client.fetch_usd_prices()

        # Estimate fees for each chain
        compute_costs: Mapping[int, ComputeCosts] = {}
        for local_chain_id, data in CHAIN_DATA.items():
            blockchain_client = self.blockchain_clients[local_chain_id]
            costs = await blockchain_client.estimate_fees()

            costs.native_value_usd = price_data[data["native"]]

            compute_costs[local_chain_id] = costs

        return compute_costs

    async def get_remote_fees(
        self, compute_costs: Mapping[int, ComputeCosts], chains_to_update: List[int]
    ) -> Mapping[int, Mapping[int, int]]:
        """Returns a dictionary of fee updates, in terms of source chain native currency, for each source chain."""

        fee_updates: Mapping[int, Mapping[int, int]] = {}
        for local_chain_id in chains_to_update:
            local_compute_costs = compute_costs.get(local_chain_id)
            remote_fee_updates: Mapping[int, int] = {}
            for remote_chain_id in CHAIN_DATA:
                if remote_chain_id != local_chain_id:
                    remote_compute_costs = compute_costs.get(remote_chain_id)

                    # Ensure prices are within the accepted tolerance
                    if remote_chain_id not in self.no_update_chains:
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
                    else:
                        # Zero values are not updated on the blockchain
                        remote_fee_in_local_native = 0

                    remote_fee_updates[remote_chain_id] = ceil(
                        remote_fee_in_local_native
                    )

            fee_updates[local_chain_id] = remote_fee_updates

        return fee_updates

    async def check_gas_price(self, chain_id: int, compute_costs: ComputeCosts) -> bool:
        """Determines if the instantaneous, remote transaction fee is within an acceptable
        range. Returns `True` if its acceptable and `False` if it's unacceptable."""

        blockchain_client = self.blockchain_clients[chain_id]
        gas_prices = await blockchain_client.get_gas_prices(
            block_count=blockchain_client.latest_blocks
        )

        if CHAIN_DATA[chain_id]["post_london_upgrade"]:
            max_fee_per_gas_list = [
                a + b
                for a, b in zip(
                    gas_prices.base_fee_per_gas_list[:-2],
                    gas_prices.max_priority_fee_per_gas_list[:-1],
                )
            ]
            median_gas_price = median(max_fee_per_gas_list)
        else:
            median_gas_price = median(gas_prices.gas_price_list)

        return (
            compute_costs.gas_price
            < median_gas_price * settings.max_acceptable_fee_multiplier
        )
