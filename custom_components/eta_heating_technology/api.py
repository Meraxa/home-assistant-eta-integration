"""API Client for eta_heating_technology."""

from __future__ import annotations

import logging
import socket
from typing import Literal

import aiohttp
import async_timeout
from pydantic_xml import BaseXmlModel, attr, element

from custom_components.eta_heating_technology.const import HTTP_OK

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

    Sanitization is necessary to avoid conflicts with the namespaces
    of the ETA values. Therefore removing the characters "." and "-" from
    any input string.

    Args:
        input_string (str): The input string to sanitize.

    Returns:
        str: The sanitized string.

    """
    return input_string.replace(".", "").replace("-", " ")


class Object(BaseXmlModel):
    """
    Represents the xml element `<object ...>` returned by the ETA heating systems api.

    E.g. `<object uri="/120/10601/0/11328/0" name="Fühler 2" />`.
    """

    uri: str = attr(name="uri")
    name: str = attr(name="name")

    @property
    def sanitized_name(self) -> str:
        """Sanitized name field."""
        return sanitize_input(self.name)

    full_name: str = ""
    namespace: str | None = None
    objects: list[Object] = element(tag="object", default=[])

    def update_namespace(self, namespace: str) -> None:
        """Update the namespace of the current object and its child objects."""
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
    """
    Represents the xml element `<fub ...>` returned by the ETA heating systems api.

    E.g. `<fub uri="/24/10561" name="Kessel">`.
    """

    uri: str = attr(name="uri")
    name: str = attr(name="name")

    @property
    def sanitized_name(self) -> str:
        """Sanitized name field."""
        return sanitize_input(self.name)

    objects: list[Object] = element(tag="object", default=[])

    def model_post_init(self) -> None:
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
    """
    Represents the xml element `<menu ...>` returned by the ETA heating systems api.

    E.g. `<menu uri="/user/menu">`.
    """

    uri: str = attr(name="uri")
    fubs: list[Fub] = element(tag="fub", default=[])

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
            "fubs": [fub.as_dict() for fub in self.fubs],
        }


class Error(BaseXmlModel):
    """
    Represents the xml element `<error ...>` returned by the ETA heating systems api.

    E.g. `<error uri="/user/var/24/10561/0/11109/1">Invalid permission</error>`.
    """

    uri: str = attr(name="uri")
    error_message: str

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
            "error_message": self.error_message,
        }


class Api(BaseXmlModel):
    """
    Represents the xml element `<api ...>` returned by the ETA heating systems api.

    E.g. `<api version="1.2" uri="/user/api"/>`.
    """

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
    Represents the xml element `<value ...>` returned by the ETA heating systems api.

    E.g. `<value advTextOffset="0" unit="°C" uri="/user/var/24/10561/0/11109/0" strValue="20" scaleFactor="10" decPlaces="0">199</value>`.

    Every <object> can be fetched with the /user/var/<uri> endpoint and thus is
    represented by the Value class.
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
        """Value scaled by the scale factor."""
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
    """
    Represents the xml element `<eta ...>` returned by the ETA heating systems api.

    E.g. `<eta xmlns="http://www.eta.co.at/rest/v1" version="1.0">`.
    """

    version: str = attr(name="version")
    api: Api | None = element(tag="api", default=None)
    value: Value | None = element(tag="value", default=None)
    menu: Menu | None = element(tag="menu", default=None)
    error: Error | None = element(tag="error", default=None)

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
    """Api Client for operations against the ETA api endpoint."""

    def __init__(  # noqa: D107
        self,
        host: str,
        port: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._host = host
        self._port = port
        self._session = session

    def build_endpoint_url(self, endpoint: str) -> str:
        """Build the endpoint URL."""
        return "http://" + self._host + ":" + str(self._port) + endpoint

    async def parse_xml_response(self, resp: aiohttp.ClientResponse) -> Eta:
        """Parse the XML response text into an Eta object."""
        text = await resp.text()
        text = text.replace('xmlns="http://www.eta.co.at/rest/v1"', "")
        text = text.encode("utf-8")
        return Eta.from_xml(text)

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

        if resp.status != HTTP_OK:
            return False

        eta = await self.parse_xml_response(resp)
        if eta.api is None:
            msg = "No API version found in response"
            raise EtaApiClientError(msg)

        return eta.api.version == "1.2"

    async def async_get_data(self, url: str) -> Value:
        """Get a value from the ETA api endpoint."""
        resp = await self._api_wrapper(method="get", url=self.build_endpoint_url(endpoint=f"/user/var/{url}"))
        eta = await self.parse_xml_response(resp)
        if eta.value is None:
            msg = "No value found in response"
            raise EtaApiClientError(msg)
        return eta.value

    async def async_parse_menu(self) -> Eta:
        """Get the xml menu listing from the ETA api and parse it to a datastructure."""
        resp = await self._api_wrapper(method="get", url=self.build_endpoint_url(endpoint="/user/menu"))
        return await self.parse_xml_response(resp)

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
