# pylint: disable=unused-argument
import pytest

from app.usecases.interfaces.repos.messages import IMessagesRepo
from app.usecases.schemas.cross_chain_message import (
    LayerZeroMessageInDb,
    LzMessage,
    WhMessage,
    WormholeMessageInDb,
)


@pytest.mark.asyncio
async def test_create_layer_zero_message(
    messages_repo: IMessagesRepo,
    inserted_lz_cross_chain_tx: int,
    test_layer_zero_message: LzMessage,
) -> None:
    await messages_repo.create_layer_zero_message(
        cross_chain_transaction_id=inserted_lz_cross_chain_tx,
        message=test_layer_zero_message,
    )

    retrieved_lz_message = await messages_repo.retrieve_layer_zero_message(
        index=test_layer_zero_message
    )

    assert isinstance(retrieved_lz_message, LayerZeroMessageInDb)
    for key, value in test_layer_zero_message.model_dump().items():
        assert value == retrieved_lz_message.model_dump()[key]


@pytest.mark.asyncio
async def test_create_wormhole_message(
    messages_repo: IMessagesRepo,
    inserted_wh_cross_chain_tx: int,
    test_wormhole_message: WhMessage,
) -> None:
    await messages_repo.create_wormhole_message(
        cross_chain_transaction_id=inserted_wh_cross_chain_tx,
        message=test_wormhole_message,
    )

    retrieved_wh_message = await messages_repo.retrieve_wormhole_message(
        index=test_wormhole_message
    )

    assert isinstance(retrieved_wh_message, WormholeMessageInDb)
    for key, value in test_wormhole_message.model_dump().items():
        assert value == retrieved_wh_message.model_dump()[key]


@pytest.mark.asyncio
async def test_retrieve_layer_zero_message(
    messages_repo: IMessagesRepo,
    test_layer_zero_message: WhMessage,
    inserted_layer_zero_message: None,
) -> None:
    retrieved_lz_message = await messages_repo.retrieve_layer_zero_message(
        index=test_layer_zero_message
    )

    assert isinstance(retrieved_lz_message, LayerZeroMessageInDb)
    for key, value in test_layer_zero_message.model_dump().items():
        assert value == retrieved_lz_message.model_dump()[key]


@pytest.mark.asyncio
async def test_retrieve_wormhole_message(
    messages_repo: IMessagesRepo,
    test_wormhole_message: WhMessage,
    inserted_wormhole_message: None,
) -> None:
    retrieved_wh_message = await messages_repo.retrieve_wormhole_message(
        index=test_wormhole_message
    )

    assert isinstance(retrieved_wh_message, WormholeMessageInDb)
    for key, value in test_wormhole_message.model_dump().items():
        assert value == retrieved_wh_message.model_dump()[key]
