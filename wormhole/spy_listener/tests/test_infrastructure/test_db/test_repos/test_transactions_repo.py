# pylint: disable=unused-argument
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
    transactions_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> None:
    transaction = await transactions_repo.create(
        transaction=create_transaction_repo_adapter
    )

    assert isinstance(transaction, TransactionsJoinRelays)
    for key, value in create_transaction_repo_adapter.dict().items():
        assert value == transaction.dict()[key]


@pytest.mark.asyncio
async def test_create_dummy(
    transactions_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> None:
    transaction_1 = await transactions_repo.create(
        transaction=create_transaction_repo_adapter
    )

    create_transaction_repo_adapter.sequence += 2

    _ = await transactions_repo.create(transaction=create_transaction_repo_adapter)

    dummy_transaction_id = transaction_1.id + 1
    dummy_transaction = await transactions_repo.retrieve(
        transaction_id=dummy_transaction_id  # The dummy
    )

    assert isinstance(dummy_transaction, TransactionsJoinRelays)
    assert dummy_transaction.from_address is None
    assert dummy_transaction.to_address is None
    assert dummy_transaction.dest_chain_id is None
    assert dummy_transaction.amount is None


@pytest.mark.asyncio
async def test_create_upsert(
    failed_transaction: int,
    transactions_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> None:
    transaction = await transactions_repo.retrieve(transaction_id=failed_transaction)

    assert transaction.to_address is None
    assert transaction.from_address is None
    assert transaction.dest_chain_id is None
    assert transaction.amount is None

    transaction = await transactions_repo.create(
        transaction=create_transaction_repo_adapter
    )

    assert isinstance(transaction, TransactionsJoinRelays)
    for key, value in create_transaction_repo_adapter.dict().items():
        assert value == transaction.dict()[key]


@pytest.mark.asyncio
async def test_retrieve(
    inserted_transaction: TransactionsJoinRelays,
    transactions_repo: ITransactionsRepo,
) -> None:
    transaction = await transactions_repo.retrieve(
        transaction_id=inserted_transaction.id
    )

    assert isinstance(transaction, TransactionsJoinRelays)
    for key, value in transaction.dict().items():
        assert value == inserted_transaction.dict()[key]


@pytest.mark.asyncio
async def test_retrieve_many(
    many_inserted_transactions: List[TransactionsJoinRelays],
    transactions_repo: ITransactionsRepo,
) -> None:
    transactions = await transactions_repo.retrieve_many(
        query_params=RetriveManyRepoAdapter(relay_status=Status.PENDING)
    )

    for transaction in transactions:
        assert isinstance(transaction, TransactionsJoinRelays)
    assert len(transactions) == constant.DEFAULT_ITERATIONS
