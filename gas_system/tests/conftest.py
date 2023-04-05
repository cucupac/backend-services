# pylint: disable=redefined-outer-name
import os

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.infrastructure.db.repos.fee_updates import FeeUpdateRepo

# import tests.constants as constant
# from app.dependencies import get_example_repo
# from app.infrastructure.db.repos.example import ExampleRepo
from app.infrastructure.web.setup import setup_app
from app.usecases.interfaces.clients.http.blockchain import IBlockchainClient
from app.usecases.interfaces.clients.http.prices import IPriceClient
from app.usecases.interfaces.repos.fee_updates import IFeeUpdateRepo
from app.usecases.interfaces.services.remote_price_manager import IRemotePriceManager
from app.usecases.services.remote_price_manager import RemotePriceManager
from tests.mocks.clients.http.coingecko import MockPriceClient

# Mocks
from tests.mocks.clients.http.evm import EvmResult, MockEvmClient

# from app.usecases.services.remote_price_manager import ExampleService


# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
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
    await test_db.execute("TRUNCATE fee_updates CASCADE")
    await test_db.disconnect()


@pytest_asyncio.fixture
async def fee_updates_repo(test_db: Database) -> IFeeUpdateRepo:
    return FeeUpdateRepo(db=test_db)


@pytest_asyncio.fixture
async def test_evm_client_success() -> IBlockchainClient:
    return MockEvmClient(result=EvmResult.SUCCESS)


@pytest_asyncio.fixture
async def test_price_client() -> IPriceClient:
    return MockPriceClient()


# Services
@pytest_asyncio.fixture
async def remote_price_manager(
    test_evm_client_success: IBlockchainClient,
    fee_updates_repo: IFeeUpdateRepo,
    test_price_client: IPriceClient,
) -> IRemotePriceManager:
    return RemotePriceManager(
        price_client=test_price_client,
        blockchain_client=test_evm_client_success,
        fee_update_repo=fee_updates_repo,
    )


# @pytest_asyncio.fixture
# async def example_service_fail(
#     test_evm_client_fail: IBlockchainClient,
#     example_repo: IExampleRepo,
# ) -> IExampleService:
#     return ExampleService(
#         example_repo=example_repo,
#         evm_client=test_evm_client_fail,
#     )


# # Database-inserted Objects


# # Repo Adapters


@pytest_asyncio.fixture
def test_app(
    # example_repo: IExampleRepo,
) -> FastAPI:
    app = setup_app()
    # app.dependency_overrides[get_example_repo] = lambda: example_repo
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")
