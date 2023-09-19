import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_client_session, get_event_loop
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.web.endpoints.metrics import health
from app.infrastructure.web.endpoints.public import points, transactions
from app.settings import settings
from app.usecases.tasks.events.startup import (
    start_award_points_task,
    start_gather_mint_events_task,
    start_gather_transfer_events_task,
    start_manage_locks_task,
    start_verify_transactions_task,
)


def setup_app():
    fastapi_app = FastAPI(
        title="Ax Protocol Relayer Gas System",
        description="Facilitates message passing between chains.",
        openapi_url=settings.openapi_url,
    )
    fastapi_app.include_router(health.router, prefix="/metrics/health")
    fastapi_app.include_router(transactions.router, prefix="/public/transactions")
    fastapi_app.include_router(points.router, prefix="/public/points")

    # CORS (Cross-Origin Resource Sharing)
    origins = ["*"]
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app


app = setup_app()


@app.on_event("startup")
async def startup_event():
    await get_event_loop()
    await get_client_session()
    await get_or_create_database()

    # Tasks
    await start_gather_transfer_events_task()
    await start_gather_mint_events_task()
    await start_verify_transactions_task()
    await start_award_points_task()
    await start_manage_locks_task()


@app.on_event("shutdown")
async def shutdown_event():
    # Close client session
    client_session = await get_client_session()
    await client_session.close()
    # Close database connection
    DATABASE = await get_or_create_database()
    if DATABASE.is_connected:
        await DATABASE.disconnect()


@click.command()
@click.option("--reload", is_flag=True)
def main(reload=False):
    kwargs = {"reload": reload}
    uvicorn.run(
        "app.infrastructure.web.setup:app",
        loop="uvloop",
        host=settings.server_host,
        port=settings.server_port,
        **kwargs,
    )
