# # pylint: disable=unused-argument
import json
import math
from typing import Mapping

import pytest
from databases import Database

import tests.constants as constant
from app.dependencies import CHAIN_DATA
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager


@pytest.mark.asyncio
async def test_remote_price_manager(
    remote_price_manager: IRemotePriceManager, test_db: Database
) -> None:
    """Test that correct values were stored in the database."""

    # Process message
    await remote_price_manager.update_remote_fees()

    for local_chain_id, local_data in CHAIN_DATA.items():
        test_fee_update = await test_db.fetch_one(
            """SELECT * FROM fee_updates WHERE fee_updates.chain_id=:chain_id
            """,
            {
                "chain_id": int(local_chain_id),
            },
        )

        # Construct expected updates dictionary here
        expected_updates: Mapping[str, int] = {}
        for remote_chain_id, remote_data in CHAIN_DATA.items():
            if remote_chain_id != local_chain_id:
                remote_cost_usd = (
                    constant.MOCK_GAS_UNITS
                    * constant.MOCK_GAS_PRICE
                    * float(constant.MOCK_USD_VALUES[remote_data["native"]])
                )
                local_cost_native = remote_cost_usd / float(
                    constant.MOCK_USD_VALUES[local_data["native"]]
                )
                expected_updates[str(remote_chain_id)] = math.ceil(local_cost_native)

        assert json.loads(test_fee_update["updates"]) == expected_updates
        assert test_fee_update["error"] is None
        assert test_fee_update["transaction_hash"] == constant.TEST_TRANSACTION_HASH
