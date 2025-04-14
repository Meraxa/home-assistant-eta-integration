"""Adds config flow for eta_heating_technology."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EtaApiClient
from .const import CONF_HOST, CONF_PORT, DOMAIN

if TYPE_CHECKING:
    from aiohttp import ClientSession


class EtaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for eta_heating_technology."""

    _errors = {}
    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            url_valid = await self._test_url(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if url_valid:
                # TODO: configure values
                pass

            self._errors["base"] = "url_broken"
            return await self._show_config_form_user(user_input)

        # Provide defaults for form
        user_input = {CONF_HOST: "0.0.0.0", CONF_PORT: "8080"}

        return await self._show_config_form_user(user_input)

    async def _show_config_form_user(self, user_input):
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
