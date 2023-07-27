# # pylint: disable=unused-argument, redefined-outer-name
import json
import math
from typing import Any, Mapping

import pytest
import pytest_asyncio
from databases import Database
from freezegun import freeze_time

import tests.constants as constant
from app.dependencies import CHAIN_DATA
from app.settings import settings
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.schemas.blockchain import AxChains, ComputeCosts
from app.usecases.schemas.fees import Status


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
            """SELECT * FROM gas_system.fee_updates AS f_u WHERE f_u.chain_id=:chain_id
            """,
            {
                "chain_id": local_chain_id,
            },
        )

        # Convert str keys to int keys
        test_fee_update_int_keys = {
            int(key): value
            for key, value in json.loads(test_fee_update["updates"]).items()
        }

        # Construct expected updates dictionary here
        expected_updates = await get_expected_fee_updates(
            local_chain_id=local_chain_id, local_data=local_data
        )

        # Assertions
        for remote_chain_id in test_fee_update_int_keys:
            assert remote_chain_id in CHAIN_DATA
            assert AxChains(remote_chain_id)

        assert test_fee_update_int_keys == expected_updates
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
            """SELECT * FROM gas_system.fee_updates AS f_u WHERE f_u.chain_id=:chain_id
            """,
            {
                "chain_id": local_chain_id,
            },
        )

        # Convert str keys to int keys
        test_fee_update_int_keys = {
            int(key): value
            for key, value in json.loads(test_fee_update["updates"]).items()
        }

        # Construct expected updates dictionary here
        expected_updates = await get_expected_fee_updates(
            local_chain_id=local_chain_id, local_data=local_data
        )

        # Assertions
        for remote_chain_id in test_fee_update_int_keys:
            assert remote_chain_id in CHAIN_DATA
            assert AxChains(remote_chain_id)

        assert test_fee_update_int_keys == expected_updates
        assert test_fee_update["error"] == constant.EVM_CLIENT_ERROR_DETAIL
        assert test_fee_update["transaction_hash"] is None
        assert test_fee_update["status"] == Status.FAILED


async def get_expected_fee_updates(
    local_chain_id: int, local_data: Mapping[int, Any]
) -> Mapping[int, int]:
    """This function is not a test; it's a helper function for calculating expected updates to
    compare actual database values to."""

    expected_updates: Mapping[int, int] = {}
    for remote_chain_id, remote_data in CHAIN_DATA.items():
        if remote_chain_id != local_chain_id:
            # Convert remote fee to local native token
            remote_cost_usd = (
                constant.MOCK_GAS_UNITS
                * constant.MOCK_GAS_PRICE
                * float(constant.MOCK_USD_VALUES[remote_data["native"]])
            )

            local_cost_native = remote_cost_usd / float(
                constant.MOCK_USD_VALUES[local_data["native"]]
            )
            # Add buffer
            if remote_chain_id != AxChains.ETHEREUM:
                local_cost_native *= settings.remote_fee_multiplier
            else:
                # Given the fronzen time for this test, we use higher multiplier
                local_cost_native *= settings.higher_ethereum_fee_multiplier

            expected_updates[remote_chain_id] = math.ceil(local_cost_native)

    return expected_updates


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_add_buffer_ethereum_high(
    remote_price_manager: IRemotePriceManager,
) -> None:
    """Test that correct buffer is applied."""

    remote_fee_pre_buffer = 1
    remote_fee_post_buffer = await remote_price_manager.add_buffer(
        remote_chain_id=AxChains.ETHEREUM,
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
        remote_chain_id=AxChains.ETHEREUM,
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
        remote_chain_id=AxChains.POLYGON,
        remote_fee_in_local_native=remote_fee_pre_buffer,
    )

    assert (
        remote_fee_post_buffer == remote_fee_pre_buffer * settings.remote_fee_multiplier
    )


@pytest_asyncio.fixture
async def test_compute_costs(
    remote_price_manager: IRemotePriceManager,
) -> Mapping[int, ComputeCosts]:
    return await remote_price_manager.get_chain_compute_costs()


@pytest.mark.asyncio
async def test_get_chain_compute_costs(
    remote_price_manager: IRemotePriceManager,
    test_compute_costs: Mapping[int, ComputeCosts],
) -> None:
    """Tests that compute costs are obtained correctly."""

    assert len(test_compute_costs) == len(CHAIN_DATA)

    for chain_id, compute_costs in test_compute_costs.items():
        assert chain_id in CHAIN_DATA
        assert AxChains(chain_id)
        assert isinstance(compute_costs, ComputeCosts)

    for chain, chain_data in CHAIN_DATA.items():
        assert (
            test_compute_costs[chain].native_value_usd
            == constant.MOCK_USD_VALUES[chain_data["native"]]
        )


@pytest.mark.asyncio
@freeze_time("2023-06-19 12:00:01", tz_offset=0)
async def test_get_remote_fees(
    remote_price_manager: IRemotePriceManager,
    test_compute_costs: Mapping[int, ComputeCosts],
) -> None:
    """Tests that compute costs are obtained correctly."""

    test_fee_updates = await remote_price_manager.get_remote_fees(
        compute_costs=test_compute_costs, chains_to_update=CHAIN_DATA.keys()
    )

    assert len(test_fee_updates) == len(CHAIN_DATA)

    for local_chain_id, remote_data in test_fee_updates.items():
        assert local_chain_id in CHAIN_DATA
        assert AxChains(local_chain_id)
        assert local_chain_id not in remote_data.keys()

        expected_remote_data = await get_expected_fee_updates(
            local_chain_id=local_chain_id, local_data=CHAIN_DATA[local_chain_id]
        )

        for remote_chain_id, native_price in remote_data.items():
            assert remote_chain_id in CHAIN_DATA
            assert AxChains(remote_chain_id)
            assert isinstance(remote_chain_id, int) and isinstance(native_price, int)
            assert native_price == expected_remote_data[remote_chain_id]
