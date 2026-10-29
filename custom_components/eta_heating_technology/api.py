"""API Client for eta_heating_technology."""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any

import aiohttp
from pydantic_xml import BaseXmlModel, attr, element

from .const import HTTP_OK

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

    def model_post_init(self, context: Any) -> None:  # noqa: ARG002
        """Automatically update namespace after model creation."""
        for obj in self.objects:
            obj.namespace = self.sanitized_name
            obj.full_name = f"{self.sanitized_name}.{obj.sanitized_name}"
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


class Success(BaseXmlModel):
    """
    Represents the xml element `<success ...>` returned by the ETA heating systems api.

    E.g. `<success uri="/user/var/78/10101/0/0/12080"/>`.
    """

    uri: str = attr(name="uri")

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "uri": self.uri,
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


def normalize_object_uri(uri: str) -> str:
    """Normalize menu/var/vars URIs to `/node/fub/...` form."""
    cleaned = uri.removeprefix("/user/var/").removeprefix("user/var/")
    cleaned = cleaned.removeprefix("/user/varinfo/").removeprefix("user/varinfo/")
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    return cleaned


def uri_path_for_varset(uri: str) -> str:
    """Return URI path without leading slash for `/user/vars/{set}/{path}`."""
    return normalize_object_uri(uri).lstrip("/")


class Value(BaseXmlModel):
    """
    Represents the xml element `<value ...>` returned by the ETA heating systems api.

    E.g. `<value advTextOffset="0" unit="°C" uri="/user/var/24/10561/0/11109/0" strValue="20" scaleFactor="10" decPlaces="0">199</value>`.

    Every <object> can be fetched with the /user/var/<uri> endpoint and thus is
    represented by the Value class.
    """

    value: str
    adv_text_offset: str = attr(name="advTextOffset")
    unit: str = attr(name="unit")
    uri: str = attr(name="uri")
    str_value: str = attr(name="strValue")
    scale_factor: str = attr(name="scaleFactor")
    dec_places: str = attr(name="decPlaces")

    @property
    def scaled_value(self) -> float | str:
        """
        Value scaled by the scale factor.

        Returns float for numeric (unit-bearing) values, str for unitless values.
        Falls back to str_value on any conversion error.
        """
        if self.unit != "":
            try:
                divisor = float(self.scale_factor)
                if divisor == 0:
                    _LOGGER.warning("scaleFactor is 0 for %s, returning raw strValue", self.uri)
                    return self.str_value
                return float(self.value) / divisor
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Cannot convert value=%r / scaleFactor=%r to float for %s, returning strValue",
                    self.value,
                    self.scale_factor,
                    self.uri,
                )
                return self.str_value
        return self.str_value

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


class Variable(BaseXmlModel, tag="variable"):
    """
    Represents `<variable ...>` inside a `/user/vars/{set}` response.

    Attributes match Value; URI is often without a leading slash.
    """

    value: str
    adv_text_offset: str = attr(name="advTextOffset", default="0")
    unit: str = attr(name="unit", default="")
    uri: str = attr(name="uri")
    str_value: str = attr(name="strValue", default="")
    scale_factor: str = attr(name="scaleFactor", default="1")
    dec_places: str = attr(name="decPlaces", default="0")

    def to_value(self) -> Value:
        """Convert to Value for shared sensor logic."""
        return Value(
            value=self.value,
            adv_text_offset=self.adv_text_offset,
            unit=self.unit,
            uri=self.uri,
            str_value=self.str_value,
            scale_factor=self.scale_factor,
            dec_places=self.dec_places,
        )


class Vars(BaseXmlModel, tag="vars"):
    """Represents `<vars uri="/user/vars/...">` (list entry or set contents)."""

    uri: str = attr(name="uri")
    variables: list[Variable] = element(tag="variable", default=[])


class ValidValue(BaseXmlModel, tag="value"):
    """A writable option listed under `<validValues>` in varinfo."""

    value: str
    str_value: str = attr(name="strValue", default="")


class ValidValues(BaseXmlModel, tag="validValues"):
    """Container for valid writable values."""

    values: list[ValidValue] = element(tag="value", default=[])


class VarInfoVariable(BaseXmlModel, tag="variable"):
    """Variable metadata from `/user/varinfo/{uri}`."""

    uri: str = attr(name="uri")
    name: str = attr(name="name", default="")
    full_name: str = attr(name="fullName", default="")
    unit: str = attr(name="unit", default="")
    dec_places: str = attr(name="decPlaces", default="0")
    scale_factor: str = attr(name="scaleFactor", default="1")
    adv_text_offset: str = attr(name="advTextOffset", default="0")
    is_writable: str = attr(name="isWritable", default="0")
    type: str | None = element(tag="type", default=None)
    valid_values: ValidValues | None = element(tag="validValues", default=None)

    @property
    def writable(self) -> bool:
        """Return True when the ETA marks the variable as writable."""
        return self.is_writable in {"1", "true", "True"}


class VarInfo(BaseXmlModel, tag="varInfo"):
    """Represents `<varInfo ...>` from `/user/varinfo/{uri}`."""

    uri: str = attr(name="uri")
    variable: VarInfoVariable | None = element(tag="variable", default=None)


class ActiveError(BaseXmlModel, tag="error"):
    """
    An active system error/warning from `/user/errors`.

    E.g. `<error msg="..." priority="Error" time="...">description</error>`.
    """

    msg: str = attr(name="msg", default="")
    priority: str = attr(name="priority", default="")
    time: str = attr(name="time", default="")
    description: str = ""


class ErrorsFub(BaseXmlModel, tag="fub"):
    """A functional block entry under `<errors>`."""

    uri: str = attr(name="uri")
    name: str = attr(name="name", default="")
    errors: list[ActiveError] = element(tag="error", default=[])


class Errors(BaseXmlModel, tag="errors"):
    """Represents `<errors uri="/user/errors">`."""

    uri: str = attr(name="uri")
    fubs: list[ErrorsFub] = element(tag="fub", default=[])

    def all_errors(self) -> list[dict[str, str]]:
        """Flatten active errors for Home Assistant attributes."""
        return [
            {
                "fub": fub.name,
                "fub_uri": fub.uri,
                "msg": err.msg,
                "priority": err.priority,
                "time": err.time,
                "description": (err.description or "").strip(),
            }
            for fub in self.fubs
            for err in fub.errors
        ]


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
    success: Success | None = element(tag="success", default=None)
    vars: Vars | None = element(tag="vars", default=None)
    var_info: VarInfo | None = element(tag="varInfo", default=None)
    errors: Errors | None = element(tag="errors", default=None)

    def as_dict(self) -> dict:
        """Convert the object to a dictionary."""
        return {
            "version": self.version,
            "api": self.api.as_dict() if self.api else None,
            "value": self.value.as_dict() if self.value else None,
            "menu": self.menu.as_dict() if self.menu else None,
            "error": self.error.as_dict() if self.error else None,
            "success": self.success.as_dict() if self.success else None,
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
        return f"http://{self._host}:{self._port}{endpoint}"

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

    async def async_update_state(self, url: str, value: str, headers: dict | None = None) -> Error | Success:
        """Update a value on the ETA api endpoint."""
        data = f"value={value}"
        resp = await self._api_wrapper(method="post", url=self.build_endpoint_url(endpoint=f"/user/var/{url}"), data=data, headers=headers)
        eta = await self.parse_xml_response(resp)
        if eta.error:
            _LOGGER.error("Error updating value: %s", eta.error.error_message)
            return eta.error
        if eta.success:
            return eta.success
        msg = "No success or error found in response"
        raise EtaApiClientError(msg)

    async def async_parse_menu(self) -> Eta:
        """Get the xml menu listing from the ETA api and parse it to a datastructure."""
        resp = await self._api_wrapper(method="get", url=self.build_endpoint_url(endpoint="/user/menu"))
        return await self.parse_xml_response(resp)

    async def async_get_varinfo(self, uri: str) -> VarInfoVariable:
        """Fetch writability metadata for a variable."""
        path = uri_path_for_varset(uri)
        resp = await self._api_wrapper(method="get", url=self.build_endpoint_url(f"/user/varinfo/{path}"))
        eta = await self.parse_xml_response(resp)
        if eta.var_info is None or eta.var_info.variable is None:
            msg = f"No varinfo found for {uri}"
            raise EtaApiClientError(msg)
        return eta.var_info.variable

    async def async_get_errors(self) -> Errors:
        """Fetch active system errors from `/user/errors`."""
        resp = await self._api_wrapper(method="get", url=self.build_endpoint_url("/user/errors"))
        eta = await self.parse_xml_response(resp)
        if eta.errors is None:
            msg = "No errors element found in response"
            raise EtaApiClientError(msg)
        return eta.errors

    async def async_create_varset(self, name: str) -> None:
        """Create a named variable set (lost after ETA reboot)."""
        await self._api_wrapper(method="put", url=self.build_endpoint_url(f"/user/vars/{name}"))

    async def async_delete_varset(self, name: str) -> None:
        """Delete a named variable set if it exists."""
        await self._api_wrapper(
            method="delete",
            url=self.build_endpoint_url(f"/user/vars/{name}"),
            raise_for_status=False,
        )

    async def async_add_to_varset(self, name: str, uri: str) -> bool:
        """
        Add a variable to a named set.

        Returns False when the ETA rejects the URI (e.g. non-pollable menu nodes).
        """
        path = uri_path_for_varset(uri)
        resp = await self._api_wrapper(
            method="put",
            url=self.build_endpoint_url(f"/user/vars/{name}/{path}"),
            raise_for_status=False,
        )
        if resp.status in {HTTP_OK, 201}:
            return True
        _LOGGER.debug("Could not add %s to varset %s (HTTP %s)", uri, name, resp.status)
        return False

    async def async_get_varset(self, name: str) -> dict[str, Value]:
        """
        Read all variables from a named set in one request.

        Returns a dict keyed by normalized object URI (`/node/fub/...`).
        """
        resp = await self._api_wrapper(
            method="get",
            url=self.build_endpoint_url(f"/user/vars/{name}"),
            raise_for_status=False,
        )
        if resp.status != HTTP_OK:
            msg = f"Variable set {name!r} not available (HTTP {resp.status})"
            raise EtaApiClientError(msg)
        eta = await self.parse_xml_response(resp)
        if eta.vars is None:
            msg = f"No vars element in response for set {name!r}"
            raise EtaApiClientError(msg)
        return {normalize_object_uri(var.uri): var.to_value() for var in eta.vars.variables}

    async def async_ensure_varset(self, name: str, uris: list[str]) -> None:
        """
        Ensure a variable set exists and contains all given URIs.

        Sets are not persisted across ETA reboots, so this may recreate them.
        """
        # Probe: if the set is readable and complete, do nothing.
        try:
            current = await self.async_get_varset(name)
        except EtaApiClientError:
            _LOGGER.debug("Variable set %s missing or incomplete, recreating", name)
            current = None
        else:
            missing = [uri for uri in uris if normalize_object_uri(uri) not in current]
            if not missing:
                return
            added = 0
            for uri in missing:
                if await self.async_add_to_varset(name, uri):
                    added += 1
            if added:
                return
            # Existing set but nothing could be added — recreate below

        await self.async_delete_varset(name)
        create_resp = await self._api_wrapper(
            method="put",
            url=self.build_endpoint_url(f"/user/vars/{name}"),
            raise_for_status=False,
        )
        if create_resp.status not in {HTTP_OK, 201}:
            msg = f"Could not create variable set {name!r} (HTTP {create_resp.status})"
            raise EtaApiClientError(msg)
        added = 0
        for uri in uris:
            if await self.async_add_to_varset(name, uri):
                added += 1
        if added == 0:
            msg = f"Variable set {name!r} is empty after adding {len(uris)} URIs"
            raise EtaApiClientError(msg)
        _LOGGER.debug("Variable set %s contains %d/%d URIs", name, added, len(uris))

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | str | None = None,
        headers: dict | None = None,
        *,
        raise_for_status: bool = True,
    ) -> aiohttp.ClientResponse:
        """Get information from the API."""
        try:
            async with asyncio.timeout(30):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                )
                if raise_for_status:
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
