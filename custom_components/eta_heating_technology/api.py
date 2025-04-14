"""API Client for eta_heating_technology."""

from __future__ import annotations

import socket

import aiohttp
import async_timeout
import xmltodict


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

        self._float_sensor_units = [
            "%",
            "A",
            "Hz",
            "Ohm",
            "Pa",
            "U/min",
            "V",
            "W",
            "W/m²",
            "bar",
            "kW",
            "kWh",
            "kg",
            "l",
            "l/min",
            "mV",
            "m²",
            "s",
            "°C",
            "%rH",
        ]

    def build_endpoint_url(self, endpoint: str) -> str:
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
