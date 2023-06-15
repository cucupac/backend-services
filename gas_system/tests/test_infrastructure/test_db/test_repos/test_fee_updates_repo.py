# pylint: disable=unused-argument
import pytest
from databases import Database

import tests.constants as constant
from app.usecases.interfaces.repos.fee_updates import IFeeUpdatesRepo

# from app.usecases.interfaces.repos.example import IExampleRepo
from app.usecases.schemas.fees import FeeUpdate, FeeUpdateInDb


@pytest.mark.asyncio
async def test_create(fee_updates_repo: IFeeUpdatesRepo, test_db: Database) -> None:
    fee_update = FeeUpdate(
        chain_id=constant.TEST_CHAIN_ID,
        updates=constant.TEST_UPDATE,
        transaction_hash=constant.TEST_TRANSACTION_HASH,
        error=None,
    )

    test_fee_update = await fee_updates_repo.create(fee_update=fee_update)

    assert isinstance(test_fee_update, FeeUpdateInDb)
    for key, value in fee_update.dict().items():
        assert value == test_fee_update.dict()[key]
