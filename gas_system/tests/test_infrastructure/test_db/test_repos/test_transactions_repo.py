# pylint: disable=unused-argument

import pytest

import tests.constants as constant
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.transactions import (
    CacheStatus,
    GrpcStatus,
    Status,
    TransactionsJoinRelays,
)


@pytest.mark.asyncio
async def test_retrieve_testing_by_chain_id(
    testing_transaction: None,
    transactions_repo: ITransactionsRepo,
) -> None:
    transaction = await transactions_repo.retrieve_testing_by_chain_id(
        chain_id=constant.TEST_DESTINATION_CHAIN_ID,
    )

    assert isinstance(transaction, TransactionsJoinRelays)
    assert transaction.relay_message == constant.TEST_VAA
    assert transaction.relay_status == Status.TESTING
    assert transaction.relay_transaction_hash is None
    assert transaction.relay_error is None
    assert transaction.relay_cache_status == CacheStatus.NEVER_CACHED
    assert transaction.relay_grpc_status == GrpcStatus.FAILED
