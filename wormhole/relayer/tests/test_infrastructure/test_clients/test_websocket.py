# pylint: disable=duplicate-code
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tests.constants as constant
from app.usecases.interfaces.services.vaa_delivery import IVaaDelivery
from app.usecases.schemas.relays import Status


@pytest.mark.asyncio
async def test_websocket(
    test_app: FastAPI, vaa_delivery_websocket: IVaaDelivery
) -> None:
    test_client = TestClient(test_app)

    with test_client.websocket_connect(
        f"/public/transactions/ws/{constant.TEST_USER_ADDRESS}"
    ) as websocket:
        mock_set_message = json.dumps(
            {
                "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
                "to_address": constant.TEST_USER_ADDRESS,
                "from_address": constant.TEST_USER_ADDRESS,
                "sequence": constant.TEST_SEQUENCE,
                "emitter_chain": constant.TEST_SOURCE_CHAIN_ID,
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "vaa_hex": constant.TEST_VAA,
            }
        ).encode()

        # Process message
        await vaa_delivery_websocket.process(set_message=mock_set_message)

        expected_data = {
            "transaction_hash": constant.TEST_TRANSACTION_HASH,
            "status": Status.SUCCESS,
            "error": None,
        }

        data = websocket.receive_json()

        assert data == expected_data


@pytest.mark.asyncio
async def test_websocket_fail(
    test_app: FastAPI, vaa_delivery_websocket_fail: IVaaDelivery
):
    test_client = TestClient(test_app)

    with test_client.websocket_connect(
        f"/public/transactions/ws/{constant.TEST_USER_ADDRESS}"
    ) as websocket:
        mock_set_message = json.dumps(
            {
                "dest_chain_id": constant.TEST_DESTINATION_CHAIN_ID,
                "to_address": constant.TEST_USER_ADDRESS,
                "from_address": constant.TEST_USER_ADDRESS,
                "sequence": constant.TEST_SEQUENCE,
                "emitter_chain": constant.TEST_SOURCE_CHAIN_ID,
                "emitter_address": constant.TEST_EMITTER_ADDRESS,
                "vaa_hex": constant.TEST_VAA,
            }
        ).encode()

        # Process message
        await vaa_delivery_websocket_fail.process(set_message=mock_set_message)

        expected_data = {
            "transaction_hash": None,
            "status": Status.FAILED,
            "error": constant.BLOCKCHAIN_CLIENT_ERROR_DETAIL,
        }

        data = websocket.receive_json()

        assert data == expected_data
