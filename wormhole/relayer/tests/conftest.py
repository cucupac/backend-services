import os
from typing import List

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

import tests.constants as constant
from app.dependencies import get_relays_repo
from app.infrastructure.db.repos.relays import TransactionsRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.queues.queue import IQueueClient
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.relays import Status
from app.usecases.schemas.transactions import CreateRepoAdapter, TransactionsJoinRelays
from app.usecases.services.vaa_delivery import VaaManager

# Mocks
from tests.mocks.clients.rabbitmq import MockRabbitmqClient


# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    return "postgres://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5444"),
        database_name=os.getenv("POSTGRES_DB", "ax_relayer_dev_test"),
    )


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
async def relays_repo(test_db: Database) -> ITransactionsRepo:
    return TransactionsRepo(db=test_db)


# Clinets
@pytest_asyncio.fixture
async def queue_client() -> IQueueClient:
    return MockRabbitmqClient()


# Services
@pytest_asyncio.fixture
async def vaa_delivery(
    queue_client: IQueueClient, relays_repo: ITransactionsRepo
) -> IVaaDelivery:
    return VaaManager(relays_repo=relays_repo, queue=queue_client)


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_transaction(
    relays_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> TransactionsJoinRelays:
    """Inserts a user object into the database for other tests."""
    return await relays_repo.create(transaction=create_transaction_repo_adapter)


@pytest_asyncio.fixture
async def many_inserted_transactions(
    relays_repo: ITransactionsRepo,
    create_transaction_repo_adapter: CreateRepoAdapter,
) -> List[TransactionsJoinRelays]:
    """Inserts a user object into the database for other tests."""

    transactions = []
    for _ in range(constant.DEFAULT_ITERATIONS):
        transactions.append(
            await relays_repo.create(transaction=create_transaction_repo_adapter)
        )

    return transactions


# Repo Adapters
@pytest_asyncio.fixture
async def create_transaction_repo_adapter() -> CreateRepoAdapter:
    return CreateRepoAdapter(
        emitter_address=constant.TEST_ADDRESS,
        from_address=constant.TEST_ADDRESS,
        to_address=constant.TEST_ADDRESS,
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
    relays_repo: ITransactionsRepo,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_relays_repo] = lambda: relays_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
