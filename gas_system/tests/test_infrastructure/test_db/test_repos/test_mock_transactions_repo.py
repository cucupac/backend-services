# pylint: disable=unused-argument

import pytest

import tests.constants as constant
from app.usecases.interfaces.repos.mock_transactions import IMockTransactionsRepo
from app.usecases.schemas.mock_transaction import MockTransactionInDb


@pytest.mark.asyncio
async def test_retrieve(
    mock_transaction: None,
    mock_transactions_repo: IMockTransactionsRepo,
) -> None:
    test_mock_transaction = await mock_transactions_repo.retrieve(
        chain_id=constant.TEST_CHAIN_ID,
    )

    assert isinstance(test_mock_transaction, MockTransactionInDb)
    assert test_mock_transaction.chain_id == constant.TEST_CHAIN_ID
    assert test_mock_transaction.payload == constant.TEST_VAA_PAYLOAD.hex()
