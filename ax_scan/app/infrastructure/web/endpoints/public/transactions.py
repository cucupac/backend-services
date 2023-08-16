from fastapi import APIRouter, Depends, HTTPException, Path

from app.dependencies import get_transactions_repo
from app.usecases.interfaces.repos.transactions import ITransactionsRepo
from app.usecases.schemas.blockchain import AxChains
from app.usecases.schemas.cross_chain_transaction import Status, TransactionResponse

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
        title="The source-chain transaction hash.",
        min_length=66,
        max_length=66,
    ),
    transaction_repo: ITransactionsRepo = Depends(get_transactions_repo),
) -> TransactionResponse:
    """This endpiont returns a cross-chain transaction object, which includes the status of the transaction."""

    cross_chain_tx = await transaction_repo.retrieve_cross_chain_tx(
        chain_id=source_chain_id, src_tx_hash=transaction_hash
    )

    if not cross_chain_tx:
        raise HTTPException(status_code=404, detail="Resource not found.")

    if (
        cross_chain_tx.source_chain_tx_status == Status.SUCCESS
        and cross_chain_tx.dest_chain_tx_status == Status.SUCCESS
    ):
        cross_chain_tx_status = Status.SUCCESS
    elif Status.FAILED in (
        cross_chain_tx.source_chain_tx_status,
        cross_chain_tx.dest_chain_tx_status,
    ):
        cross_chain_tx_status = Status.FAILED
    else:
        cross_chain_tx_status = Status.PENDING

    cross_chain_tx_raw = cross_chain_tx.model_dump()
    return TransactionResponse(**cross_chain_tx_raw, status=cross_chain_tx_status)
