"""Adds config flow for eta_heating_technology."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)

from .api import Eta, EtaApiClient, EtaApiClientError, Fub, Object, Value
from .const import (
    CHOSEN_BINARY_SENSORS,
    CHOSEN_ENTITIES,
    CHOSEN_SWITCHES,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    EtaSensorType,
)
from .utils import determine_sensor_type

_LOGGER = logging.getLogger(__name__)

CHOSEN_FUBS = "chosen_fubs"

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from homeassistant.config_entries import ConfigFlowResult


def _get_objects_recursively(data: Fub | Object) -> list[Object]:
    """Get all objects recursively from the data."""
    objects: list[Object] = []
    if isinstance(data, (Fub, Object)):
        for obj in data.objects:
            objects.extend(_get_objects_recursively(obj))
        if isinstance(data, Object):
            objects.append(data)
    return objects


async def classify_eta_entities(
    client: EtaApiClient,
    objects: list[Object],
) -> tuple[list[str], list[str], list[str]]:
    """
    Classify objects into sensors, writable switches, and read-only binaries.

    Uses `/user/varinfo` `isWritable` for on/off endpoints. Returns
    `(sensor_names, switch_candidates, binary_sensor_names)`.
    """
    sem = asyncio.Semaphore(3)

    async def _fetch(obj: Object) -> tuple[Object, Value | None]:
        async with sem:
            try:
                return obj, await client.async_get_data(obj.uri)
            except Exception:  # noqa: BLE001
                _LOGGER.debug("Could not fetch value for %s", obj.full_name)
                return obj, None

    results = await asyncio.gather(*[_fetch(obj) for obj in objects])

    sensor_names: list[str] = []
    switch_names: list[str] = []
    binary_names: list[str] = []

    async def _classify_binary(obj: Object) -> None:
        try:
            info = await client.async_get_varinfo(obj.uri)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("varinfo failed for %s, treating as binary sensor", obj.full_name)
            binary_names.append(obj.full_name)
            return
        if info.writable:
            switch_names.append(obj.full_name)
        else:
            binary_names.append(obj.full_name)

    for obj, value in results:
        if value is None:
            sensor_names.append(obj.full_name)
            continue
        sensor_type = determine_sensor_type(value)
        if sensor_type is EtaSensorType.BINARY_SENSOR:
            async with sem:
                await _classify_binary(obj)
        else:
            sensor_names.append(obj.full_name)

    _LOGGER.debug(
        "Classified %d sensors, %d switch candidates, %d binary sensors",
        len(sensor_names),
        len(switch_names),
        len(binary_names),
    )
    return sensor_names, switch_names, binary_names


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
        self.selected_fub_names: list[str] = []
        self.sensor_names: list[str] = []
        self.switch_names: list[str] = []
        self.binary_sensor_names: list[str] = []

    def as_dict(self) -> dict:
        """Convert the configuration flow data to a dictionary."""
        return {
            CONF_HOST: self.host,
            CONF_PORT: self.port,
            CHOSEN_ENTITIES: [obj.as_dict() for obj in self.chosen_entities],
            CHOSEN_SWITCHES: self.switch_names,
            CHOSEN_BINARY_SENSORS: self.binary_sensor_names,
        }


class EtaFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for eta_heating_technology."""

    VERSION = 1
    configuration_flow_data: ConfigurationFlowData

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry,  # noqa: ANN001, ARG004
    ) -> EtaOptionsFlowHandler:
        """Get the options flow for this handler."""
        return EtaOptionsFlowHandler()

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self._errors = {}

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()

            try:
                if await self._test_url(user_input[CONF_HOST], user_input[CONF_PORT]):
                    possible_endpoints: Eta = await self._get_possible_endpoints(user_input[CONF_HOST], user_input[CONF_PORT])
                    self.configuration_flow_data = ConfigurationFlowData(
                        host=user_input[CONF_HOST],
                        port=user_input[CONF_PORT],
                        discovered_entities=possible_endpoints,
                    )
                    return await self.async_step_select_fubs()
            except EtaApiClientError as exception:
                _LOGGER.debug("ETA API not reachable: %s", exception)

            self._errors["base"] = "url_broken"

        return await self._show_config_form_user(user_input or {CONF_PORT: "8080"})

    async def async_step_select_fubs(self, user_input: dict | None = None) -> ConfigFlowResult:
        """First selection step: choose Fubs (entity groups) to include."""
        self._errors = {}
        fubs = self._get_fubs()

        if user_input is not None:
            selected = user_input.get(CHOSEN_FUBS, [])
            if not selected:
                self._errors["base"] = "no_fubs_selected"
                return await self._show_config_form_fubs(fubs)
            self.configuration_flow_data.selected_fub_names = selected
            return await self.async_step_select_entities()

        return await self._show_config_form_fubs(fubs)

    async def async_step_select_entities(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Second selection step: choose individual entities within selected Fubs."""
        self._errors = {}
        fubs = self._get_fubs()

        # Filter objects to only those from selected fubs
        objects: list[Object] = []
        for fub in fubs:
            if fub.sanitized_name in self.configuration_flow_data.selected_fub_names:
                objects.extend(_get_objects_recursively(fub))

        all_names = [obj.full_name for obj in objects]

        if user_input is not None:
            if not user_input[CHOSEN_ENTITIES]:
                self._errors["base"] = "no_entities_selected"
                return await self._show_config_form_endpoint(objects, defaults=all_names)

            self.configuration_flow_data.chosen_entities = [obj for obj in objects if obj.full_name in user_input[CHOSEN_ENTITIES]]

            # Classify entities by fetching their values + varinfo
            session = async_get_clientsession(self.hass)
            client = EtaApiClient(
                host=self.configuration_flow_data.host,
                port=self.configuration_flow_data.port,
                session=session,
            )
            sensor_names, switch_names, binary_names = await classify_eta_entities(
                client,
                self.configuration_flow_data.chosen_entities,
            )
            self.configuration_flow_data.sensor_names = sensor_names
            self.configuration_flow_data.switch_names = switch_names
            self.configuration_flow_data.binary_sensor_names = binary_names

            if switch_names:
                return await self.async_step_confirm_switches()

            # No writable switches — skip confirmation
            _LOGGER.debug(
                "Selected entities: %s",
                [obj.full_name for obj in self.configuration_flow_data.chosen_entities],
            )
            return self.async_create_entry(
                title=f"ETA at {self.configuration_flow_data.host}",
                data=self.configuration_flow_data.as_dict(),
            )

        # Pre-select all entities from chosen fubs
        return await self._show_config_form_endpoint(objects, defaults=all_names)

    async def async_step_confirm_switches(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Third step: confirm which writable on/off entities become switches."""
        self._errors = {}
        if user_input is not None:
            confirmed_switches = user_input.get(CHOSEN_SWITCHES, [])
            deselected = [name for name in self.configuration_flow_data.switch_names if name not in confirmed_switches]
            self.configuration_flow_data.switch_names = confirmed_switches
            # Deselected writable endpoints become read-only binary sensors
            self.configuration_flow_data.binary_sensor_names = list(dict.fromkeys([*self.configuration_flow_data.binary_sensor_names, *deselected]))
            _LOGGER.debug(
                "Final entities (sensors=%d, switches=%d, binaries=%d): %s",
                len(self.configuration_flow_data.sensor_names),
                len(confirmed_switches),
                len(self.configuration_flow_data.binary_sensor_names),
                [obj.full_name for obj in self.configuration_flow_data.chosen_entities],
            )
            return self.async_create_entry(
                title=f"ETA at {self.configuration_flow_data.host}",
                data=self.configuration_flow_data.as_dict(),
            )

        return self.async_show_form(
            step_id="confirm_switches",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CHOSEN_SWITCHES,
                        default=self.configuration_flow_data.switch_names,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self.configuration_flow_data.switch_names,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=self._errors,
        )

    def _get_fubs(self) -> list[Fub]:
        """Get fubs from discovered entities."""
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
        return fubs

    async def _show_config_form_user(self, user_input: dict) -> ConfigFlowResult:
        """Show the configuration form to edit host and port data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, vol.UNDEFINED)): str,
                    vol.Required(CONF_PORT, default=user_input.get(CONF_PORT, vol.UNDEFINED)): str,
                }
            ),
            errors=self._errors,
        )

    async def _show_config_form_fubs(
        self,
        fubs: list[Fub],
        defaults: list[str] | None = None,
    ) -> ConfigFlowResult:
        """Show the form to select Fubs (entity groups)."""
        fub_options = [
            selector.SelectOptionDict(
                value=fub.sanitized_name,
                label=f"{fub.name} ({len(_get_objects_recursively(fub))})",
            )
            for fub in fubs
        ]
        return self.async_show_form(
            step_id="select_fubs",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CHOSEN_FUBS,
                        default=defaults or [],
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=fub_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=self._errors,
        )

    async def _show_config_form_endpoint(
        self,
        objects: list[Object],
        defaults: list[str] | None = None,
    ) -> ConfigFlowResult:
        """Show the configuration form to select which endpoints should become entities."""
        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CHOSEN_ENTITIES,
                        default=defaults or [],
                    ): selector.SelectSelector(
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


class EtaOptionsFlowHandler(OptionsFlow):
    """
    Handle options flow for ETA Heating Technology.

    Allows the user to modify which entities are monitored
    without creating a new config entry.
    """

    def __init__(self) -> None:
        """Initialize the options flow."""
        self._errors: dict[str, str] = {}
        self._discovered_fubs: list[Fub] = []
        self._selected_fub_names: list[str] = []
        self._chosen_objects: list[Object] = []
        self._sensor_names: list[str] = []
        self._switch_names: list[str] = []
        self._binary_sensor_names: list[str] = []

    async def async_step_init(
        self,
        user_input: dict | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Handle the initial step — discover entities from the ETA device."""
        host = self.config_entry.data[CONF_HOST]
        port = self.config_entry.data[CONF_PORT]
        session = async_get_clientsession(self.hass)
        eta_client = EtaApiClient(host=host, port=port, session=session)

        try:
            discovered: Eta = await eta_client.async_parse_menu()
        except EtaApiClientError:
            return self.async_abort(reason="cannot_connect")

        if discovered.menu is None or not discovered.menu.fubs:
            return self.async_abort(reason="no_entities")

        self._discovered_fubs = discovered.menu.fubs
        return await self.async_step_select_fubs()

    async def async_step_select_fubs(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Select Fubs (entity groups) in options flow."""
        self._errors = {}
        # Determine which fubs have currently chosen entities (for pre-selection)
        current_fub_names: list[str] = []
        for obj in self.config_entry.data.get(CHOSEN_ENTITIES, []):
            full_name = obj.get("full_name", "") if isinstance(obj, dict) else obj.full_name
            fub_name = full_name.split(".")[0] if "." in full_name else full_name
            if fub_name and fub_name not in current_fub_names:
                current_fub_names.append(fub_name)

        if user_input is not None:
            selected = user_input.get(CHOSEN_FUBS, [])
            if not selected:
                self._errors["base"] = "no_fubs_selected"
            else:
                self._selected_fub_names = selected
                return await self.async_step_select_entities()

        fub_options = [
            selector.SelectOptionDict(
                value=fub.sanitized_name,
                label=f"{fub.name} ({len(_get_objects_recursively(fub))})",
            )
            for fub in self._discovered_fubs
        ]
        return self.async_show_form(
            step_id="select_fubs",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CHOSEN_FUBS,
                        default=current_fub_names,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=fub_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=self._errors,
        )

    async def async_step_select_entities(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Select individual entities within chosen Fubs in options flow."""
        errors: dict[str, str] = {}

        # Get objects only from selected fubs
        objects: list[Object] = []
        for fub in self._discovered_fubs:
            if fub.sanitized_name in self._selected_fub_names:
                objects.extend(_get_objects_recursively(fub))

        all_names = [obj.full_name for obj in objects]

        # Determine currently configured entity names
        current_entity_names: list[str] = []
        for obj_data in self.config_entry.data.get(CHOSEN_ENTITIES, []):
            name = obj_data.get("full_name", "") if isinstance(obj_data, dict) else obj_data.full_name
            current_entity_names.append(name)

        if user_input is not None:
            if not user_input.get(CHOSEN_ENTITIES):
                errors["base"] = "no_entities_selected"
            else:
                self._chosen_objects = [obj for obj in objects if obj.full_name in user_input[CHOSEN_ENTITIES]]

                host = self.config_entry.data[CONF_HOST]
                port = self.config_entry.data[CONF_PORT]
                client = EtaApiClient(host=host, port=port, session=async_get_clientsession(self.hass))
                sensor_names, switch_names, binary_names = await classify_eta_entities(client, self._chosen_objects)
                self._sensor_names = sensor_names
                self._switch_names = switch_names
                self._binary_sensor_names = binary_names

                if switch_names:
                    return await self.async_step_confirm_switches()

                # No writable switches — save directly
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **self.config_entry.data,
                        CHOSEN_ENTITIES: [obj.as_dict() for obj in self._chosen_objects],
                        CHOSEN_SWITCHES: [],
                        CHOSEN_BINARY_SENSORS: binary_names,
                    },
                )
                return self.async_create_entry(title="", data={})

        # Build defaults: existing entities stay selected, new fubs get all selected
        previously_configured_fubs = {(n.split(".")[0] if "." in n else n) for n in current_entity_names}
        defaults = []
        for name in all_names:
            fub_name = name.split(".")[0] if "." in name else name
            if fub_name in previously_configured_fubs:
                if name in current_entity_names:
                    defaults.append(name)
            else:
                # New fub — pre-select all its entities
                defaults.append(name)

        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CHOSEN_ENTITIES,
                        default=defaults,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=all_names,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_confirm_switches(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Confirm which writable on/off entities become switches."""
        self._errors = {}
        if user_input is not None:
            confirmed = user_input.get(CHOSEN_SWITCHES, [])
            deselected = [name for name in self._switch_names if name not in confirmed]
            binary_names = list(dict.fromkeys([*self._binary_sensor_names, *deselected]))
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    CHOSEN_ENTITIES: [obj.as_dict() for obj in self._chosen_objects],
                    CHOSEN_SWITCHES: confirmed,
                    CHOSEN_BINARY_SENSORS: binary_names,
                },
            )
            return self.async_create_entry(title="", data={})

        # Keep earlier decisions: entities configured before as read-only stay unselected
        previous_switches: list[str] | None = self.config_entry.data.get(CHOSEN_SWITCHES)
        previous_binaries = set(self.config_entry.data.get(CHOSEN_BINARY_SENSORS) or [])
        configured_names = {obj.get("full_name", "") for obj in self.config_entry.data.get(CHOSEN_ENTITIES, [])}
        default_switches = [
            name
            for name in self._switch_names
            if name not in previous_binaries and (previous_switches is None or name in previous_switches or name not in configured_names)
        ]

        return self.async_show_form(
            step_id="confirm_switches",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CHOSEN_SWITCHES,
                        default=default_switches,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._switch_names,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            multiple=True,
                        )
                    )
                }
            ),
            errors=self._errors,
        )
