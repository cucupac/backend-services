from fastapi import APIRouter, Body, Depends

from app.dependencies import get_transactions_repo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.transactions import TransactionBase

transactions_router = APIRouter(tags=["Transactions"])


@transactions_router.post(
    "/actions/create",
    status_code=201,
    response_model=None,
)
async def create(
    body: TransactionBase = Body(...),
    transactions_repo: ITransactionsRepo = Depends(get_transactions_repo),
) -> None:
    """Saves transaction."""

    await transactions_repo.create(transaction=body)
