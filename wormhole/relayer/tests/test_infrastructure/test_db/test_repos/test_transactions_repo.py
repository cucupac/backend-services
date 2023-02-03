from typing import List

import pytest

import tests.constants as constant
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.relays import Status
from app.usecases.schemas.transactions import (
    CreateRepoAdapter,
    RetriveManyRepoAdapter,
    TransactionsJoinRelays,
)


@pytest.mark.asyncio
async def test_create(
    relays_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> None:

    transaction = await relays_repo.create(transaction=create_transaction_repo_adapter)

    assert isinstance(transaction, TransactionsJoinRelays)
    for key, value in create_transaction_repo_adapter.dict().items():
        assert value == transaction.dict()[key]


@pytest.mark.asyncio
async def test_retrieve(
    inserted_transaction: TransactionsJoinRelays,
    relays_repo: ITransactionsRepo,
) -> None:

    transaction = await relays_repo.retrieve(id=inserted_transaction.id)

    assert isinstance(transaction, TransactionsJoinRelays)
    for key, value in transaction.dict().items():
        assert value == inserted_transaction.dict()[key]


@pytest.mark.asyncio
async def test_retrieve_many(
    many_inserted_transactions: List[TransactionsJoinRelays],
    relays_repo: ITransactionsRepo,
) -> None:

    transactions = await relays_repo.retrieve_many(
        query_params=RetriveManyRepoAdapter(relay_status=Status.PENDING)
    )

    for transaction in transactions:
        assert isinstance(transaction, TransactionsJoinRelays)
    assert len(transactions) == constant.DEFAULT_ITERATIONS
