"""API Client for eta_heating_technology."""

from __future__ import annotations

import socket

import aiohttp
import async_timeout
import xmltodict

from custom_components.eta_heating_technology.const import ETA_SENSOR_UNITS


class EtaApiClientError(Exception):
    """Exception to indicate a general API error."""


class EtaApiClientCommunicationError(
    EtaApiClientError,
):
    """Exception to indicate a communication error."""


class EtaApiClientAuthenticationError(
    EtaApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise EtaApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class EtaApiClient:
    """Sample API Client."""

    def __init__(
        self,
        host: str,
        port: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._host = host
        self._port = port
        self._session = session

    def build_endpoint_url(self, endpoint: str) -> str:
        """Build the endpoint URL."""
        return "http://" + self._host + ":" + str(self._port) + endpoint

    async def does_endpoint_exists(self) -> bool:
        """
        Check if the ETA API is reachable and if the API version is correct.

        This is done by sending a request to the /user/api endpoint.

        Returns:
            bool: True, if the endpoint is reachable and correct api version,
            otherwise False.

        """
        resp = await self._api_wrapper(
            method="get",
            url=self.build_endpoint_url("/user/api"),
        )

        if resp.status != 200:
            return False

        # Check if the response is valid XML
        parsed_response = xmltodict.parse(await resp.text())
        api_version = parsed_response["eta"]["api"]["@version"]
        return api_version == "1.2"

    def evaluate_xml_dict(self, xml_dict, uri_dict, prefix=""):
        if type(xml_dict) is list:
            for child in xml_dict:
                self.evaluate_xml_dict(child, uri_dict, prefix)
        elif "object" in xml_dict:
            child = xml_dict["object"]
            new_prefix = f"{prefix} {xml_dict['@name']}"
            # add parent to uri_dict and evaluate childs then
            key = f"{prefix} {xml_dict['@name']}".strip().lower().replace(" ", "_")
            uri_dict[key] = {
                "url": xml_dict["@uri"],
                "name": f"{prefix} {xml_dict['@name']}".strip(),
            }
            self.evaluate_xml_dict(child, uri_dict, new_prefix)
        else:
            key = f"{prefix} {xml_dict['@name']}".strip().lower().replace(" ", "_")
            uri_dict[key] = {
                "url": xml_dict["@uri"],
                "name": f"{prefix} {xml_dict['@name']}".strip(),
            }

    def _parse_data(self, data):
        unit = data["@unit"]
        if unit in ETA_SENSOR_UNITS:
            scale_factor = int(data["@scaleFactor"])
            raw_value = float(data["#text"])
            value = raw_value / scale_factor
        else:
            # use default text string representation for values that cannot be parsed properly
            value = data["@strValue"]
        return value, unit

    async def async_get_data(self, url: str):
        data = await self._api_wrapper(
            method="get", url=self.build_endpoint_url(endpoint=f"/user/var/{url}")
        )
        text = await data.text()
        data = xmltodict.parse(text)["eta"]["value"]
        return self._parse_data(data)

    async def async_get_value_unit(self, url: str):
        """Get the value and unit of a sensor."""
        data = await self._api_wrapper(
            method="get", url=self.build_endpoint_url(endpoint=f"/user/var/{url}")
        )
        text = await data.text()
        data = xmltodict.parse(text)["eta"]["value"]["@unit"]
        return data

    async def get_raw_sensor_dict(self):
        data = await self._api_wrapper(
            method="get", url=self.build_endpoint_url(endpoint="/user/menu")
        )
        text = await data.text()
        data = xmltodict.parse(text)
        raw_dict = data["eta"]["menu"]["fub"]
        return raw_dict

    async def get_sensors_dict(self):
        raw_dict = await self.get_raw_sensor_dict()
        uri_dict = {}
        self.evaluate_xml_dict(raw_dict, uri_dict)
        return uri_dict

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> aiohttp.ClientResponse:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return response

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise EtaApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise EtaApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise EtaApiClientError(
                msg,
            ) from exception
