import aiohttp
import pytest
from custom_components.eta_heating_technology.api import EtaApiClient

VALID_VERSION_REQUEST = """<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">
    <api version="1.2" uri="/user/api"/>
</eta>
"""
INVALID_VERSION_REQUEST = """<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">
    <api version="1.0" uri="/user/api"/>
</eta>
"""
NO_RESPONSE_REQUEST = """"""


class TestResponse:
    def __init__(self, status, text):
        self.status = status
        self._text = text

    async def text(self):
        return self._text


def mock_get_request(response_status, response_text):
    async def _mock(*args, **kwargs):
        return TestResponse(response_status, response_text)

    return _mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_status, response_text, expected_result",
    [
        (200, VALID_VERSION_REQUEST, True),
        (200, INVALID_VERSION_REQUEST, False),
        (404, NO_RESPONSE_REQUEST, False),
    ],
)
async def test_does_endpoint_exists(
    monkeypatch, response_status, response_text, expected_result
):
    monkeypatch.setattr(
        EtaApiClient,
        "_api_wrapper",
        mock_get_request(response_status, response_text),
    )
    eta = EtaApiClient(
        host="192.168.178.59",
        port="8080",
        session=aiohttp.ClientSession(),
    )

    resp = await eta.does_endpoint_exists()
    assert resp == expected_result
