"""API Client for eta_heating_technology."""

from __future__ import annotations

import logging
import socket
from typing import List, Literal, Optional

import aiohttp
import async_timeout
from pydantic_xml import BaseXmlModel, attr, element

_LOGGER = logging.getLogger(__name__)


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


def sanitize_input(input_string: str) -> str:
    """
    Sanitize the input string by removing unwanted characters.

    Args:
        input_string (str): The input string to sanitize.

    Returns:
        str: The sanitized string.
    """
    # Remove unwanted characters
    sanitized_string = input_string.replace(".", "").replace("-", " ")
    return sanitized_string


class Object(BaseXmlModel):
    uri: str = attr(name="uri")
    name: str = attr(name="name")

    @property
    def sanitized_name(self) -> str:
        """Sanitize the name field."""
        return sanitize_input(self.name)

    full_name: str = ""
    namespace: Optional[str] = None
    objects: List[Object] = element(tag="object", default=[])

    def update_namespace(self, namespace: str) -> None:
        """Update the namespace of the object."""
        self.namespace = namespace
        self.full_name = f"{namespace}.{self.sanitized_name}"
        if self.objects:
            for obj in self.objects:
                obj.update_namespace(self.full_name)

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
            "name": self.name,
            "sanitized_name": self.sanitized_name,
            "full_name": self.full_name,
            "namespace": self.namespace,
            "objects": [obj.as_dict() for obj in self.objects],
        }


class Fub(BaseXmlModel):
    uri: str = attr(name="uri")
    name: str = attr(name="name")

    @property
    def sanitized_name(self) -> str:
        """Sanitize the name field."""
        return sanitize_input(self.name)

    objects: List[Object] = element(tag="object", default=[])

    def model_post_init(self, __context) -> None:
        """Automatically update namespace after model creation."""
        for obj in self.objects:
            obj.namespace = self.sanitized_name
            obj.full_name = f"{self.name}.{obj.sanitized_name}"
            if obj.objects:
                obj.update_namespace(obj.namespace)

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
            "name": self.name,
            "sanitized_name": self.sanitized_name,
            "objects": [obj.as_dict() for obj in self.objects],
        }


class Menu(BaseXmlModel):
    uri: str = attr(name="uri")
    fubs: List[Fub] = element(tag="fub", default=[])

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
            "fubs": [fub.as_dict() for fub in self.fubs],
        }


class Error(BaseXmlModel):
    uri: str = attr(name="uri")
    error_message: str

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
            "error_message": self.error_message,
        }


class Api(BaseXmlModel):
    version: str = attr(name="version")
    uri: str = attr(name="uri")

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "version": self.version,
            "uri": self.uri,
        }


class Value(BaseXmlModel):
    """
    Value class to represent the value of an object.

    Every <object> can be fetched with the /user/var/<uri> endpoint and
    thus is represented by the Value class.
    """

    value: str
    adv_text_offset: str = attr(name="advTextOffset")
    unit: Literal[
        "°C",
        "W",
        "A",
        "Hz",
        "Pa",
        "V",
        "W/m²",
        "bar",
        "kW",
        "kWh",
        "kg",
        "mV",
        "s",
        "%rH",
        "m³/h",
        "",
    ] = attr(name="unit")
    uri: str = attr(name="uri")
    str_value: str = attr(name="strValue")
    scale_factor: str = attr(name="scaleFactor")
    dec_places: str = attr(name="decPlaces")

    @property
    def scaled_value(self) -> str:
        """Sanitize the name field."""
        if self.unit != "":
            return str(float(self.value) / float(self.scale_factor))
        return self.unit

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "value": self.value,
            "adv_text_offset": self.adv_text_offset,
            "unit": self.unit,
            "uri": self.uri,
            "str_value": self.str_value,
            "scale_factor": self.scale_factor,
            "dec_places": self.dec_places,
        }


class Eta(BaseXmlModel, tag="eta"):
    version: str = attr(name="version")
    api: Optional[Api] = element(tag="api", default=None)
    value: Optional[Value] = element(tag="value", default=None)
    menu: Optional[Menu] = element(tag="menu", default=None)
    error: Optional[Error] = element(tag="error", default=None)

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "version": self.version,
            "api": self.api.as_dict() if self.api else None,
            "value": self.value.as_dict() if self.value else None,
            "menu": self.menu.as_dict() if self.menu else None,
            "error": self.error.as_dict() if self.error else None,
        }


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

    async def does_endpoint_exist(self) -> bool:
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

        # TODO @Meraxa: Replace with static value
        if resp.status != 200:
            return False

        # Check if the response is valid XML
        text = await resp.text()
        text = text.replace('xmlns="http://www.eta.co.at/rest/v1"', "")
        eta = Eta.from_xml(text)
        if eta.api is None:
            raise EtaApiClientError("No API version found in response")

        return eta.api.version == "1.2"

    async def async_get_data(self, url: str) -> Value:
        data = await self._api_wrapper(
            method="get", url=self.build_endpoint_url(endpoint=f"/user/var/{url}")
        )
        text = await data.text()
        text = text.replace('xmlns="http://www.eta.co.at/rest/v1"', "")
        eta = Eta.from_xml(text)
        if eta.value is None:
            raise EtaApiClientError("No value found in response")
        return eta.value

    async def async_parse_menu(self):
        data = await self._api_wrapper(
            method="get", url=self.build_endpoint_url(endpoint="/user/menu")
        )
        text = await data.text()
        text = text.replace('xmlns="http://www.eta.co.at/rest/v1"', "")
        eta = Eta.from_xml(text)
        return eta

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
