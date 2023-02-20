import base64
import json
import math
from typing import Mapping

from app.settings import settings
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import ComputeCosts
from app.usecases.schemas.fees import MinimumFees


class RemotePriceManager(IRemotePriceManager):
    def __init__(
        self, price_client: IPriceClient, blockchain_client: IBlockchainClient
    ):
        self.price_client = price_client
        self.blockchain_client = blockchain_client

    async def update_remote_prices(self) -> None:
        """Updates gas prices for remote computation in local native token."""

        chain_lookup: Mapping[str, Mapping[str, str]] = json.loads(
            base64.b64decode(settings.chain_lookup).decode("utf-8")
        )

        # Estimate fees for each chain
        compute_costs = dict()
        for chain_id in chain_lookup:
            compute_costs[chain_id] = await self.blockchain_client.estimate_fees(
                chain_id=chain_id
            )

        # Construct fee information
        fee_updates = dict()
        for local_chain_id, local_chain_data in chain_lookup.items():
            local_native_price_data = await self.price_client.fetch_prices(
                asset_symbol=local_chain_data["native"]
            )
            remote_fees = []
            remote_chain_ids = []
            for remote_chain_id, remote_chain_data in chain_lookup.items():
                if remote_chain_id != local_chain_id:
                    local_native_priced_in_remote = local_native_price_data[
                        remote_chain_data["native"]
                    ]
                    remote_compute_costs = compute_costs[remote_chain_id]
                    remote_fee_in_local_native = (
                        remote_compute_costs.gas_units
                        * remote_compute_costs.gas_price
                        / local_native_priced_in_remote
                    )
                    remote_fees.append(math.ceil(remote_fee_in_local_native))
                    remote_chain_ids.append(remote_chain_id)
            fee_updates[local_chain_id] = MinimumFees(
                remote_chain_ids=remote_chain_ids, fees=remote_fees
            )

        # Update remote fees on local chains
        for chain_id, remote_data in fee_updates.items():
            transaction_hash = await self.blockchain_client.update_fees(
                remote_data=remote_data, local_chain_id=chain_id
            )
