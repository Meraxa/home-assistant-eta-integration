import aiohttp
import pytest

from custom_components.eta_heating_technology.api import (
    Error,
    Eta,
    EtaApiClient,
    Fub,
    Menu,
    Object,
    Success,
    Value,
)
from custom_components.eta_heating_technology.const import EtaSensorType
from custom_components.eta_heating_technology.sensor import determine_sensor_type

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
    def __init__(self, status, text) -> None:
        self.status = status
        self._text = text

    async def text(self):
        return self._text


def mock_get_request(response_status, response_text):
    async def _mock(*args, **kwargs):
        return TestResponse(response_status, response_text)

    return _mock

def mock_update_state(response_status, response_text):
    async def _mock(*args, **kwargs):
        return TestResponse(response_status, response_text)

    return _mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response_status", "response_text", "expected_result"),
    [
        (200, VALID_VERSION_REQUEST, True),
        (200, INVALID_VERSION_REQUEST, False),
        (404, NO_RESPONSE_REQUEST, False),
    ],
)
async def test_does_endpoint_exist(
    monkeypatch, response_status, response_text, expected_result
) -> None:
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

    resp = await eta.does_endpoint_exist()
    assert resp == expected_result


MENUE_RESPONSE = """
<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">
    <menu uri="/user/menu">
        <fub uri="/24/10561" name="Kessel">
            <object uri="/24/10561/0/0/10990" name="Eingänge">
                <object uri="/24/10561/0/11031/0" name="Wassermangel">
                    <object uri="/24/10561/0/11031/2012" name="Einschalt Verzögerung"/>
                    <object uri="/24/10561/0/11031/2013" name="Ausschalt Verzögerung"/>
                    <object uri="/24/10561/0/11031/2016" name="Eingang"/>
                </object>
            </object>
        </fub>
        <fub uri="/24/10571" name="Part.-Absch.">
            <object uri="/24/10571/0/0/10990" name="Eingänge">
                <object uri="/24/10571/0/0/14439" name="Verriegelung Hochspannungsnetzteil"/>
                <object uri="/24/10571/0/0/14440" name="Verriegelung Hochspannungsnetzteil 2"/>
                <object uri="/24/10571/0/0/14453" name="Verriegelung Hochspannungsnetzteil rechts"/>
            </object>
        </fub>
    </menu>
</eta>
"""


MENUE_RESPONSE_MODEL = Eta(
    version="1.0",
    menu=Menu(
        uri="/user/menu",
        fubs=[
            Fub(
                uri="/24/10561",
                name="Kessel",
                objects=[
                    Object(
                        uri="/24/10561/0/0/10990",
                        name="Eingänge",
                        full_name="Kessel.Eingänge",
                        namespace="Kessel",
                        objects=[
                            Object(
                                uri="/24/10561/0/11031/0",
                                name="Wassermangel",
                                full_name="Kessel.Eingänge.Wassermangel",
                                namespace="Kessel.Eingänge",
                                objects=[
                                    Object(
                                        uri="/24/10561/0/11031/2012",
                                        name="Einschalt Verzögerung",
                                        full_name="Kessel.Eingänge.Wassermangel.Einschalt Verzögerung",
                                        namespace="Kessel.Eingänge.Wassermangel",
                                        objects=[],
                                    ),
                                    Object(
                                        uri="/24/10561/0/11031/2013",
                                        name="Ausschalt Verzögerung",
                                        full_name="Kessel.Eingänge.Wassermangel.Ausschalt Verzögerung",
                                        namespace="Kessel.Eingänge.Wassermangel",
                                        objects=[],
                                    ),
                                    Object(
                                        uri="/24/10561/0/11031/2016",
                                        name="Eingang",
                                        full_name="Kessel.Eingänge.Wassermangel.Eingang",
                                        namespace="Kessel.Eingänge.Wassermangel",
                                        objects=[],
                                    ),
                                ],
                            )
                        ],
                    )
                ],
            ),
            Fub(
                uri="/24/10571",
                name="Part.-Absch.",
                objects=[
                    Object(
                        uri="/24/10571/0/0/10990",
                        name="Eingänge",
                        full_name="Part Absch.Eingänge",
                        namespace="Part Absch",
                        objects=[
                            Object(
                                uri="/24/10571/0/0/14439",
                                name="Verriegelung Hochspannungsnetzteil",
                                full_name="Part Absch.Eingänge.Verriegelung Hochspannungsnetzteil",
                                namespace="Part Absch.Eingänge",
                                objects=[],
                            ),
                            Object(
                                uri="/24/10571/0/0/14440",
                                name="Verriegelung Hochspannungsnetzteil 2",
                                full_name="Part Absch.Eingänge.Verriegelung Hochspannungsnetzteil 2",
                                namespace="Part Absch.Eingänge",
                                objects=[],
                            ),
                            Object(
                                uri="/24/10571/0/0/14453",
                                name="Verriegelung Hochspannungsnetzteil rechts",
                                full_name="Part Absch.Eingänge.Verriegelung Hochspannungsnetzteil rechts",
                                namespace="Part Absch.Eingänge",
                                objects=[],
                            ),
                        ],
                    )
                ],
            ),
        ],
    ),
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response_status", "response_text", "expected_result"),
    [
        (200, MENUE_RESPONSE, MENUE_RESPONSE_MODEL),
    ],
)
async def test_get_menu(monkeypatch, response_status, response_text, expected_result) -> None:
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

    resp = await eta.async_parse_menu()
    assert resp == expected_result


TEST_2 = """
<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">
    <value advTextOffset="0" unit="°C" uri="/user/var/120/10102/0/11060/0" strValue="40" scaleFactor="10" decPlaces="0">403</value>
</eta>
"""

TEST_3 = """
<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">
    <value advTextOffset="1802" unit="" uri="/user/var/78/10101/0/0/12080" strValue="Aus" scaleFactor="1" decPlaces="0">1802</value>
</eta>
"""

TEST_4 = """
<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">
    <value advTextOffset="2000" unit="" uri="/user/var/24/10561/0/0/12000" strValue="Heizen" scaleFactor="1" decPlaces="0">2006</value>
</eta>
"""

TEST_2_EX = Value(
    value="403",
    adv_text_offset="0",
    unit="°C",
    uri="/user/var/120/10102/0/11060/0",
    str_value="40",
    scale_factor="10",
    dec_places="0",
)

TEST_3_EX = Value(
    value="1802",
    adv_text_offset="1802",
    unit="",
    uri="/user/var/78/10101/0/0/12080",
    str_value="Aus",
    scale_factor="1",
    dec_places="0",
)

TEST_4_EX = Value(
    value="2006",
    adv_text_offset="2000",
    unit="",
    uri="/user/var/24/10561/0/0/12000",
    str_value="Heizen",
    scale_factor="1",
    dec_places="0",
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response_status", "response_text", "expected_result"),
    [
        (200, TEST_2, TEST_2_EX),
        (200, TEST_3, TEST_3_EX),
        (200, TEST_4, TEST_4_EX),
    ],
)
async def test_get_data(monkeypatch, response_status, response_text, expected_result) -> None:
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

    resp = await eta.async_get_data("")
    assert resp == expected_result

TURN_HEAT_CIRCUIT_ON_RESPONSE_SUCCESS = """
<eta version="1.0" xmlns="http://www.eta.co.at/rest/v1">
    <success uri="/user/var/78/10101/0/0/12080"/>
</eta>
"""

TURN_HEAT_CIRCUIT_ON_RESPONSE_ERROR = """
<eta version="1.0" xmlns="http://www.eta.co.at/rest/v1">
    <error uri="/user/var/78/10101/0/0/12080">Value is out of range.</error>
</eta>
"""

TURN_HEAT_CIRCUIT_ON_RESPONSE_SUCCESS_EX = Success(
    uri="/user/var/78/10101/0/0/12080",
)

TURN_HEAT_CIRCUIT_ON_RESPONSE_ERROR_EX = Error(
    uri="/user/var/78/10101/0/0/12080",
    error_message="Value is out of range.",
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response_status", "response_text", "expected_result"),
    [
        (200, TURN_HEAT_CIRCUIT_ON_RESPONSE_SUCCESS, TURN_HEAT_CIRCUIT_ON_RESPONSE_SUCCESS_EX),
        (200, TURN_HEAT_CIRCUIT_ON_RESPONSE_ERROR, TURN_HEAT_CIRCUIT_ON_RESPONSE_ERROR_EX),
    ],
)
async def test_update_state(monkeypatch, response_status, response_text, expected_result) -> None:
    monkeypatch.setattr(
        EtaApiClient,
        "_api_wrapper",
        mock_update_state(response_status, response_text),
    )
    eta = EtaApiClient(
        host="192.168.178.59",
        port="8080",
        session=aiohttp.ClientSession(),
    )

    resp = await eta.async_update_state("uri", "value")
    assert resp == expected_result

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("value", "expected_sensor_type"),
    [
        (TEST_2_EX, EtaSensorType.SENSOR),
        (TEST_3_EX, EtaSensorType.BINARY_SENSOR),
        (TEST_4_EX, EtaSensorType.STRING_SENSOR),
    ],
)
async def test_determine_sensor_type(value: Value, expected_sensor_type: EtaSensorType) -> None:
    resp = determine_sensor_type(value)
    assert resp == expected_sensor_type
