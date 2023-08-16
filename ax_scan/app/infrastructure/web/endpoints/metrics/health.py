from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Metrics"])


@router.get("")
async def health_check():
    return {"status": "healthy", "datetime": datetime.now().isoformat()}
