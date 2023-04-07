from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.fee_updates import FeeUpdateRepo
from app.usecases.interfaces.repos.fee_updates import IFeeUpdateRepo


async def get_fee_update_repo() -> IFeeUpdateRepo:
    return FeeUpdateRepo(db=await get_or_create_database())
