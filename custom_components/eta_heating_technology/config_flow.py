"""Adds config flow for eta_heating_technology."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)

from .api import Eta, EtaApiClient, EtaApiClientError, Fub, Object
from .const import (
    CHOSEN_ENTITIES,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from homeassistant.config_entries import ConfigFlowResult


class ConfigurationFlowData:
    """Class to hold the configuration flow data."""

    def __init__(
        self,
        host: str,
        port: str,
        discovered_entities: Eta,
        chosen_entities: list[Object] | None = None,
    ) -> None:
        """Initialize the configuration flow data."""
        if chosen_entities is None:
            chosen_entities = []
        self.host: str = host
        self.port: str = port
        self.discovered_entities: Eta = discovered_entities
        self.chosen_entities: list[Object] = chosen_entities

    def as_dict(self) -> dict:
        """Convert the configuration flow data to a dictionary."""
        return {
            CONF_HOST: self.host,
            CONF_PORT: self.port,
            CHOSEN_ENTITIES: self.chosen_entities,
        }


class EtaFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for eta_heating_technology."""

    VERSION = 1
    configuration_flow_data: ConfigurationFlowData

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self._errors = {}

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            url_valid = await self._test_url(user_input[CONF_HOST], user_input[CONF_PORT])
            if url_valid:
                possible_endpoints: Eta = await self._get_possible_endpoints(user_input[CONF_HOST], user_input[CONF_PORT])
                self.configuration_flow_data = ConfigurationFlowData(
                    host=user_input[CONF_HOST],
                    port=user_input[CONF_PORT],
                    discovered_entities=possible_endpoints,
                )

                return await self.async_step_select_entities()

            self._errors["base"] = "url_broken"

        # Provide defaults for form
        user_input = {CONF_HOST: "0.0.0.0", CONF_PORT: "8080"}  # noqa: S104

        return await self._show_config_form_user(user_input)

    def get_objects_recursively(self, data: Fub | Object) -> list[Object]:
        """Get all objects recursively from the data."""
        objects: list[Object] = []
        if isinstance(data, (Fub, Object)):
            for obj in data.objects:
                objects.extend(self.get_objects_recursively(obj))
            if isinstance(data, Object):
                objects.append(data)
        return objects

    async def async_step_select_entities(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Second step in config flow to add a repo to watch."""
        if self.configuration_flow_data.discovered_entities is None:
            msg = "No discovered entities found"
            raise EtaApiClientError(msg)
        menu = self.configuration_flow_data.discovered_entities.menu
        if menu is None:
            msg = "No menu found in response"
            raise EtaApiClientError(msg)
        fubs = menu.fubs
        if fubs is None:
            msg = "No fubs found in response"
            raise EtaApiClientError(msg)

        objects: list[Object] = []
        for fub in fubs:
            # Get all objects recursively from the fub
            objects.extend(self.get_objects_recursively(fub))

        if user_input is not None:
            # Check if the user has selected at least one entity
            if not user_input[CHOSEN_ENTITIES]:
                self._errors["base"] = "no_entities_selected"
                return await self._show_config_form_endpoint(objects)

            # Add the keys of the selected entities to the data dict if the name is in
            # the user_input
            self.configuration_flow_data.chosen_entities = [obj for obj in objects if obj.full_name in user_input[CHOSEN_ENTITIES]]

            # Add this line to log the selected entities
            _LOGGER.info(
                "self.configuration_flow_data.chosen_entities: %s",
                self.configuration_flow_data.chosen_entities,
            )

            # User is done, create the config entry.
            return self.async_create_entry(
                title=f"ETA at {self.configuration_flow_data.host}",
                data=self.configuration_flow_data.as_dict(),
            )
        return await self._show_config_form_endpoint(objects)

    async def _show_config_form_user(self, user_input: dict) -> ConfigFlowResult:
        """Show the configuration form to edit host and port data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_PORT, default=user_input[CONF_PORT]): str,
                }
            ),
            errors=self._errors,
        )

    async def _show_config_form_endpoint(self, objects: list[Object]) -> ConfigFlowResult:
        """Show the configuration form to select which endpoints should become entities."""
        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(CHOSEN_ENTITIES): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[obj.full_name for obj in objects],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=self._errors,
        )

    async def _get_possible_endpoints(self, host: str, port: str) -> Eta:
        """
        Request the available endpoints from the ETA API.

        This is done by sending a request to the /user/menu endpoint.

        Args:
            host (str): The host IP address of the ETA API, e.g. `192.168.178.21`.
            port (int): The port of the ETA API, e.g. `8080`.

        Returns:
            Eta: The parsed ETA object containing the available endpoints.

        """
        session: ClientSession = async_get_clientsession(self.hass)
        eta_client = EtaApiClient(host=host, port=port, session=session)
        return await eta_client.async_parse_menu()

    async def _test_url(self, host: str, port: str) -> bool:
        """
        Test if the URL and port of the ETA API are reachable.

        Args:
            host (str): The host IP address of the ETA API, e.g. `192.168.178.21`.
            port (int): The port of the ETA API, e.g. `8080`.

        Returns:
            bool: True if the URL is reachable, False otherwise.

        """
        session: ClientSession = async_get_clientsession(self.hass)
        eta_client = EtaApiClient(host=host, port=port, session=session)
        return await eta_client.does_endpoint_exist()
