import pytest

from app.dependencies import get_vaa_delivery
from app.settings import settings
from app.usecases.services.vaa_delivery import VaaDelivery


@pytest.mark.asyncio
async def test_get_vaa_delivery(test_db_url: str) -> None:
    settings.db_url = test_db_url

    test_vaa_delivery = await get_vaa_delivery()

    assert isinstance(test_vaa_delivery, VaaDelivery)
