# pylint: disable=unused-argument
import pytest

import tests.constants as constant
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo
from app.usecases.schemas.fees import FeeUpdate, FeeUpdateInDb, Status


@pytest.mark.asyncio
async def test_create(
    fee_updates_repo: IFeeUpdatesRepo, test_fee_update: FeeUpdate
) -> None:
    created_fee_update = await fee_updates_repo.create(fee_update=test_fee_update)

    assert isinstance(created_fee_update, FeeUpdateInDb)
    for key, value in test_fee_update.dict().items():
        assert value == created_fee_update.dict()[key]


@pytest.mark.asyncio
async def test_retrieve(
    fee_updates_repo: IFeeUpdatesRepo, test_fee_update: FeeUpdate
) -> None:
    created_fee_update = await fee_updates_repo.create(fee_update=test_fee_update)

    retrieved_fee_update = await fee_updates_repo.retrieve(
        fee_update_id=created_fee_update.id
    )

    assert isinstance(retrieved_fee_update, FeeUpdateInDb)
    for key, value in retrieved_fee_update.dict().items():
        assert value == retrieved_fee_update.dict()[key]


@pytest.mark.asyncio
async def test_retrieve_last_update_by_chain_id(
    fee_updates_repo: IFeeUpdatesRepo, test_fee_update: FeeUpdate
) -> None:
    created_fee_updates = []
    for i in range(constant.DEFAULT_ITERATIONS):
        if i == constant.DEFAULT_ITERATIONS - 1:
            test_fee_update.status = Status.FAILED
        created_fee_update = await fee_updates_repo.create(fee_update=test_fee_update)
        created_fee_updates.append(created_fee_update)

    retrieved_fee_update = await fee_updates_repo.retrieve_last_update_by_chain_id(
        chain_id=constant.TEST_CHAIN_ID
    )

    assert retrieved_fee_update == created_fee_updates[-1]
    assert retrieved_fee_update.status == Status.FAILED
