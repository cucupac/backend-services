from fastapi import APIRouter
from fastapi import APIRouter, Depends, Path, HTTPException

from app.dependencies import get_transactions_repo, bridge_data
from app.usecases.interfaces.repos.transactions import ICrossChainTransactionsRepo
from app.usecases.schemas.transactions import TransactionResponse
from app.usecases.schemas.blockchain import AxChains


router = APIRouter(tags=["Transactions"])


@router.get(
    "/{source_chain_id}/{transaction_hash}",
    status_code=200,
    response_model=TransactionResponse,
)
async def get_transaction(
    source_chain_id: AxChains = Path(..., title="The actual ID of the source chain."),
    transaction_hash: str = Path(
        ...,
        title="The source-chain transaction's transaction hash.",
        min_length=66,
        max_length=66,
    ),
    transaction_repo: ICrossChainTransactionsRepo = Depends(get_transactions_repo),
) -> TransactionResponse:
    """This endpiont returns a cross-chain transaction object, which includes the status of the transaction."""

    transaction = await transaction_repo.retrieve(
        source_chain_id=source_chain_id, transaction_hash=transaction_hash
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Resource not found")

    return TransactionResponse(**transaction.model_dump())
