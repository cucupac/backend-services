import pytest

from app.usecases.interfaces.repos.transactions import IExample


@pytest.mark.asyncio
async def test_example(
    example_repo: IExample,
) -> None:
    assert True
