import click
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import get_client_session, get_event_loop, get_redis_client
from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.web.endpoints.metrics import health
from app.settings import settings
from app.usecases.tasks.events.startup import (
    start_gather_missed_task,
    start_gather_pending_task,
    start_manage_locks_task,
    start_retry_failed_task,
    start_verify_delivery_task,
)


def setup_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="Ax Protocol Wormhole Relayer",
        description="Facilitates message passing between chains.",
        openapi_url=settings.openapi_url,
    )
    fastapi_app.include_router(health.health_router, prefix="/metrics/health")

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
async def startup_event() -> None:
    await get_event_loop()
    await get_client_session()
    await get_or_create_database()
    await get_redis_client()
    # Tasks
    await start_retry_failed_task()
    await start_gather_missed_task()
    await start_gather_pending_task()
    await start_verify_delivery_task()
    await start_manage_locks_task()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    # Close client session
    client_session = await get_client_session()
    await client_session.close()
    # Close database connection
    DATABASE = await get_or_create_database()
    if DATABASE.is_connected:
        await DATABASE.disconnect()


@click.command()
@click.option("--reload", is_flag=True)
def main(reload=False) -> None:
    kwargs = {"reload": reload}
    uvicorn.run(
        "app.infrastructure.web.setup:app",
        loop="uvloop",
        host=settings.server_host,
        port=settings.server_port,
        **kwargs,
    )
