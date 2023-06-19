# # pylint: disable=unused-argument
import json
import math
from typing import Any, Mapping

import pytest
from databases import Database
from freezegun import freeze_time

import tests.constants as constant
from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import Chains
from app.usecases.schemas.fees import FeeUpdateError, Status


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_remote_price_manager(
    remote_price_manager: IRemotePriceManager, test_db: Database
) -> None:
    """Test that correct values were stored in the database."""

    # Process message
    await remote_price_manager.update_remote_fees(
        chains_to_update=constant.MOCK_CHAINS_TO_UPDATE
    )

    for local_chain_id, local_data in CHAIN_DATA.items():
        test_fee_update = await test_db.fetch_one(
            """SELECT * FROM fee_updates WHERE fee_updates.chain_id=:chain_id
            """,
            {
                "chain_id": int(local_chain_id),
            },
        )

        # Construct expected updates dictionary here
        expected_updates = await get_expected_fee_updates(
            local_chain_id=local_chain_id, local_data=local_data
        )

        assert json.loads(test_fee_update["updates"]) == expected_updates
        assert test_fee_update["error"] is None
        assert test_fee_update["transaction_hash"] == constant.TEST_TRANSACTION_HASH
        assert test_fee_update["status"] == Status.SUCCESS


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_remote_price_manager_fail(
    remote_price_manager_failed: IRemotePriceManager, test_db: Database
) -> None:
    """Test that correct values were stored in the database."""

    # Process message
    await remote_price_manager_failed.update_remote_fees(
        chains_to_update=constant.MOCK_CHAINS_TO_UPDATE
    )

    for local_chain_id, local_data in CHAIN_DATA.items():
        test_fee_update = await test_db.fetch_one(
            """SELECT * FROM fee_updates WHERE fee_updates.chain_id=:chain_id
            """,
            {
                "chain_id": int(local_chain_id),
            },
        )

        # Construct expected updates dictionary here
        expected_updates = await get_expected_fee_updates(
            local_chain_id=local_chain_id, local_data=local_data
        )

        assert json.loads(test_fee_update["updates"]) == expected_updates
        assert test_fee_update["error"] == constant.EVM_CLIENT_ERROR_DETAIL
        assert test_fee_update["transaction_hash"] is None
        assert test_fee_update["status"] == Status.FAILED


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_remote_price_manager_median_testing(
    remote_price_manager_median_testing: IRemotePriceManager, test_db: Database
) -> None:
    """Test that correct values were stored in the database. This test assumes that
    Ethereum is the only chain with an instantaneous gas price out of distribution. Therefore,
    Ethereum's remote destination price on all non-Ethereum chains should be 0, and the transaction
    on Ethereum should be marked as `failed`."""

    # Process message
    await remote_price_manager_median_testing.update_remote_fees(
        chains_to_update=constant.MOCK_CHAINS_TO_UPDATE
    )

    for local_chain_id, local_data in CHAIN_DATA.items():
        test_fee_update = await test_db.fetch_one(
            """SELECT * FROM fee_updates WHERE fee_updates.chain_id=:chain_id
            """,
            {
                "chain_id": int(local_chain_id),
            },
        )

        # Construct expected updates dictionary here
        expected_updates = await get_expected_fee_updates(
            local_chain_id=local_chain_id, local_data=local_data, median_test=True
        )

        assert json.loads(test_fee_update["updates"]) == expected_updates
        assert test_fee_update["status"] == Status.FAILED
        if local_chain_id == Chains.ETHEREUM:
            assert test_fee_update["error"] == FeeUpdateError.TX_FEE_TOO_HIGH
            assert test_fee_update["transaction_hash"] is None
        else:
            assert test_fee_update["error"] == FeeUpdateError.DESTINATION_PRICE_TOO_HIGH
            assert test_fee_update["transaction_hash"] is not None


async def get_expected_fee_updates(
    local_chain_id: int, local_data: Mapping[str, Any], median_test: bool = False
) -> Mapping[int, int]:
    """This function is not a test; it's a helper function for calculating expected updates to
    compare actual database values to."""

    expected_updates: Mapping[str, int] = {}
    for remote_chain_id, remote_data in CHAIN_DATA.items():
        if remote_chain_id != local_chain_id:
            if median_test and remote_chain_id == constant.TEST_TOO_EXPENSIVE_CHAIN:
                remote_cost_usd = 0
            else:
                remote_cost_usd = (
                    constant.MOCK_GAS_UNITS
                    * constant.MOCK_GAS_PRICE
                    * float(constant.MOCK_USD_VALUES[remote_data["native"]])
                )
            local_cost_native = remote_cost_usd / float(
                constant.MOCK_USD_VALUES[local_data["native"]]
            )

            # Add buffer if Ethereum is not involved.
            if remote_chain_id != Chains.ETHEREUM:
                local_cost_native *= settings.remote_fee_multiplier
            else:
                # Given the fronzen time for this test, we use higher multiplier
                local_cost_native *= settings.higher_ethereum_fee_multiplier

            expected_updates[str(remote_chain_id)] = math.ceil(local_cost_native)

    return expected_updates


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_add_buffer_ethereum_high(
    remote_price_manager: IRemotePriceManager,
) -> None:
    """Test that correct buffer is applied."""

    remote_fee_pre_buffer = 1
    remote_fee_post_buffer = await remote_price_manager.add_buffer(
        remote_chain_id=Chains.ETHEREUM,
        remote_fee_in_local_native=remote_fee_pre_buffer,
    )

    assert (
        remote_fee_post_buffer
        == remote_fee_pre_buffer * settings.higher_ethereum_fee_multiplier
    )


@pytest.mark.asyncio
@freeze_time("2023-06-19 18:00:01", tz_offset=0)
async def test_add_buffer_ethereum_low(
    remote_price_manager: IRemotePriceManager,
) -> None:
    """Test that correct buffer is applied."""

    remote_fee_pre_buffer = 1
    remote_fee_post_buffer = await remote_price_manager.add_buffer(
        remote_chain_id=Chains.ETHEREUM,
        remote_fee_in_local_native=remote_fee_pre_buffer,
    )

    assert (
        remote_fee_post_buffer
        == remote_fee_pre_buffer * settings.lower_ethereum_fee_multiplier
    )


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_add_buffer_non_ethereum(
    remote_price_manager: IRemotePriceManager,
) -> None:
    """Test that correct buffer is applied."""

    remote_fee_pre_buffer = 1
    remote_fee_post_buffer = await remote_price_manager.add_buffer(
        remote_chain_id=Chains.POLYGON, remote_fee_in_local_native=remote_fee_pre_buffer
    )

    assert (
        remote_fee_post_buffer == remote_fee_pre_buffer * settings.remote_fee_multiplier
    )


@pytest.mark.asyncio
async def test_check_gas_prices(
    remote_price_manager_median_testing: IRemotePriceManager,
) -> None:
    """Test that gas check gas prices returns true when instantaneous gas prices is not too high."""

    chain_compute_costs = (
        await remote_price_manager_median_testing.get_chain_compute_costs()
    )

    for chain_id in CHAIN_DATA:
        is_acceptable = await remote_price_manager_median_testing.check_gas_price(
            chain_id=chain_id, compute_costs=chain_compute_costs[chain_id]
        )
        if chain_id == constant.TEST_TOO_EXPENSIVE_CHAIN:
            assert not is_acceptable
        else:
            assert is_acceptable
