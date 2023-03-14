import math
from typing import Mapping

from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.interfaces.repos.fee_updates import IFeeUpdateRepo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import BlockchainClientError, ComputeCosts
from app.usecases.schemas.fees import FeeUpdate, MinimumFees


class RemotePriceManager(IRemotePriceManager):
    def __init__(
        self,
        price_client: IPriceClient,
        blockchain_client: IBlockchainClient,
        fee_update_repo: IFeeUpdateRepo,
    ):
        self.price_client = price_client
        self.blockchain_client = blockchain_client
        self.fee_update_repo = fee_update_repo

    # pylint: disable = too-many-locals
    async def update_remote_fees(self) -> None:
        """Updates gas prices for remote computation in local native token."""

        # Estimate fees for each chain
        compute_costs: Mapping[int, ComputeCosts] = {}
        for local_chain_id, data in CHAIN_DATA.items():
            costs = await self.blockchain_client.estimate_fees(chain_id=local_chain_id)
            price_data = await self.price_client.fetch_prices(
                asset_symbol=data["native"]
            )
            costs.native_value_usd = float(price_data.get("USD"))
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
                    remote_fee_updates[remote_chain_id] = math.ceil(
                        remote_fee_in_local_native
                    )
            fee_updates[local_chain_id] = remote_fee_updates

            for chain_id, remote_fee_updates in fee_updates.items():
                try:
                    transaction_hash_bytes = await self.blockchain_client.update_fees(
                        remote_data=MinimumFees(
                            remote_chain_ids=list(remote_fee_updates.keys()),
                            remote_fees=list(remote_fee_updates.values()),
                        ),
                        local_chain_id=chain_id,
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
