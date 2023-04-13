# pylint: disable=redefined-outer-name
import os
from typing import List

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

import tests.constants as constant
from app.dependencies import get_transactions_repo, logger
from app.infrastructure.db.repos.transactions import TransactionsRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.unique_set import IUniqueSetClient
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.vaa_manager import IVaaManager
from app.usecases.schemas.relays import Status
from app.usecases.schemas.transactions import CreateRepoAdapter, TransactionsJoinRelays
from app.usecases.services.vaa_manager import VaaManager

# Mocks
from tests.mocks.clients.unique_set import MockUniqueSetClient, UniqueSetResult


# Database Connection
@pytest_asyncio.fixture
async def test_db_url() -> str:
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5444")
    database_name = os.getenv("POSTGRES_DB", "ax_relayer_dev_test")
    return f"postgres://{username}:{password}@{host}:{port}/{database_name}"


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE transactions CASCADE")
    await test_db.execute("TRUNCATE relays CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def transactions_repo(test_db: Database) -> ITransactionsRepo:
    return TransactionsRepo(db=test_db)


# Clients
@pytest_asyncio.fixture
async def test_unique_set_client_success() -> IUniqueSetClient:
    return MockUniqueSetClient(result=UniqueSetResult.SUCCESS)


@pytest_asyncio.fixture
async def test_unique_set_client_fail() -> IUniqueSetClient:
    return MockUniqueSetClient(result=UniqueSetResult.FAILURE)


# Services
@pytest_asyncio.fixture
async def vaa_manager(
    test_unique_set_client_success: IUniqueSetClient,
    transactions_repo: ITransactionsRepo,
) -> IVaaManager:
    return VaaManager(
        transactions_repo=transactions_repo,
        unique_set=test_unique_set_client_success,
        logger=logger,
    )


@pytest_asyncio.fixture
async def vaa_manager_unique_set_fail(
    test_unique_set_client_fail: IUniqueSetClient, transactions_repo: ITransactionsRepo
) -> IVaaManager:
    return VaaManager(
        transactions_repo=transactions_repo,
        unique_set=test_unique_set_client_fail,
        logger=logger,
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_transaction(
    transactions_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> TransactionsJoinRelays:
    """Inserts a user object into the database for other tests."""
    return await transactions_repo.create(transaction=create_transaction_repo_adapter)


sequence_count = 0


@pytest_asyncio.fixture
async def many_inserted_transactions(
    transactions_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> List[TransactionsJoinRelays]:
    """Inserts a user object into the database for other tests."""

    global sequence_count  # pylint: disable = global-statement
    transactions = []
    for _ in range(constant.DEFAULT_ITERATIONS):
        transaction = create_transaction_repo_adapter
        transaction.sequence += sequence_count
        transactions.append(await transactions_repo.create(transaction=transaction))
        sequence_count += 1

    return transactions


# Repo Adapters
@pytest_asyncio.fixture
async def create_transaction_repo_adapter() -> CreateRepoAdapter:
    return CreateRepoAdapter(
        emitter_address=constant.TEST_EMITTER_ADDRESS,
        from_address=constant.TEST_USER_ADDRESS,
        to_address=constant.TEST_USER_ADDRESS,
        source_chain_id=constant.TEST_SOURCE_CHAIN_ID,
        dest_chain_id=constant.TEST_DESTINATION_CHAIN_ID,
        amount=constant.TEST_AMOUNT,
        sequence=0,
        relay_status=Status.PENDING,
        relay_error=None,
        relay_message=constant.TEST_VAA,
    )


@pytest_asyncio.fixture
def test_app(
    transactions_repo: ITransactionsRepo,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_transactions_repo] = lambda: transactions_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
