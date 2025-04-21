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

from .api import EtaApiClient
from .const import (
    CHOSEN_ENTITIES,
    CONF_HOST,
    CONF_PORT,
    DISCOVERED_ENTITIES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from homeassistant.config_entries import ConfigFlowResult


class EtaFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for eta_heating_technology."""

    _errors = {}
    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            url_valid = await self._test_url(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if url_valid:
                self.data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    DISCOVERED_ENTITIES: await self._get_possible_endpoints(
                        user_input[CONF_HOST], user_input[CONF_PORT]
                    ),
                    CHOSEN_ENTITIES: [],
                }

                return await self.async_step_select_entities()

            self._errors["base"] = "url_broken"

        # Provide defaults for form
        user_input = {CONF_HOST: "192.168.178.59", CONF_PORT: "8080"}

        return await self._show_config_form_user(user_input)

    async def async_step_select_entities(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Second step in config flow to add a repo to watch."""
        if user_input is not None:
            # Add the keys of the selected entities to the data dict if the name is in
            # the user_input
            dat: dict = self.data[DISCOVERED_ENTITIES]
            self.data[CHOSEN_ENTITIES] = [
                key
                for key, value in dat.items()
                if value["name"] in user_input[CHOSEN_ENTITIES]
            ]

            # Check if the user has selected at least one entity
            if not self.data[CHOSEN_ENTITIES]:
                self._errors["base"] = "no_entities_selected"
                return await self._show_config_form_endpoint(
                    self.data[DISCOVERED_ENTITIES]
                )

            # Add this line to log the selected entities
            _LOGGER.info("self.data[CHOSEN_ENTITIES]: %s", self.data[CHOSEN_ENTITIES])

            # User is done, create the config entry.
            return self.async_create_entry(
                title=f"ETA at {self.data[CONF_HOST]}", data=self.data
            )

        return await self._show_config_form_endpoint(self.data[DISCOVERED_ENTITIES])

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

    async def _show_config_form_endpoint(self, endpoint_dict: dict) -> ConfigFlowResult:
        """Show the configuration form to select which endpoints should become entities."""
        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(CHOSEN_ENTITIES): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                endpoint_dict[key]["name"] for key in endpoint_dict
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=self._errors,
        )

    async def _get_possible_endpoints(self, host: str, port: str) -> dict:
        """
        Request the available endpoints from the ETA API.

        This is done by sending a request to the /user/menu endpoint.

        Args:
            host (str): The host IP address of the ETA API, e.g. `192.168.178.21`.
            port (int): The port of the ETA API, e.g. `8080`.

        Returns:
            dict: Dictionary with the available endpoints with the name of the sensor as
                key and the endpoint as value.
                Example: `{"Sensor 1": "/user/var/1", "Sensor 2": "/user/var/2"}`.

        """
        session: ClientSession = async_get_clientsession(self.hass)
        eta_client = EtaApiClient(host=host, port=port, session=session)
        return await eta_client.get_sensors_dict()

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
        return await eta_client.does_endpoint_exists()
