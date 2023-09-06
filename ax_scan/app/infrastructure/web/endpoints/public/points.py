from eth_utils import is_checksum_address
from fastapi import APIRouter, Depends, HTTPException, Path

from app.dependencies import get_points_repo
from app.usecases.interfaces.repos.points import IPointsRepo
from app.usecases.schemas.points import PointsResponse

router = APIRouter(tags=["Points"])


@router.get(
    "/{account}",
    status_code=200,
    response_model=PointsResponse,
)
async def get_points(
    account: str = Path(
        ...,
        title="A user's account.",
        min_length=42,
        max_length=42,
    ),
    points_repo: IPointsRepo = Depends(get_points_repo),
) -> PointsResponse:
    """This endpiont returns a user's current points."""

    if not is_checksum_address(account):
        raise HTTPException(status_code=400, detail="Invalid account.")

    points = await points_repo.retrieve(account=account)

    if not points:
        return PointsResponse(account=account, points=0)

    return PointsResponse(account=account, points=points.points)
