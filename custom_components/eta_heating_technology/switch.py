"""Switch platform for eta_heating_technology."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .api import Error, Success, Value
from .const import (
    ETA_BINARY_SENSOR_VALUES_DE,
    EtaSensorType,
    EtaSwitchStates,
)
from .utils import determine_sensor_type
from .entity import EtaEntity

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import EtaApiClient

    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: EtaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = config_entry.runtime_data.coordinator
    api_client = config_entry.runtime_data.client

    # Use coordinator's cached objects to avoid re-parsing every time
    chosen_objects = coordinator.chosen_objects
    _LOGGER.debug("switch_keys: %s", chosen_objects)

    eta_switches: list[EtaSwitch] = []
    for obj in chosen_objects:
        if coordinator.data and obj.full_name in coordinator.data:
            value = coordinator.data[obj.full_name]
        else:
            value = await api_client.async_get_data(obj.uri)
        sensor_type = determine_sensor_type(value)

        if sensor_type is EtaSensorType.BINARY_SENSOR:
            eta_switches.append(
                EtaSwitch(
                    coordinator=coordinator,
                    api_client=api_client,
                    entity_description=SwitchEntityDescription(
                        key=obj.full_name,
                        name=obj.full_name,
                    ),
                    config_entry_id=config_entry.entry_id,
                    url=obj.uri,
                )
            )

    async_add_entities(eta_switches)


class EtaSwitch(EtaEntity, SwitchEntity):
    """eta_heating_technology Switch class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        api_client: EtaApiClient,
        config_entry_id: str,
        entity_description: SwitchEntityDescription,
        url: str,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        # Add the config entry id to the unique id to avoid conflicts with
        # multiple eta installations
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self.url = url
        self.api_client = api_client
        self.coordinator = coordinator

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        response = await self.api_client.async_update_state(
            url=self.url, value=EtaSwitchStates.ON.value, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if isinstance(response, Error):
            _LOGGER.error("Failed to turn on switch %s: %s", self._attr_unique_id, response.error_message)
        if isinstance(response, Success):
            _LOGGER.info("Successfully turned on switch %s", self._attr_unique_id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        response = await self.api_client.async_update_state(
            url=self.url, value=EtaSwitchStates.OFF.value, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if isinstance(response, Error):
            _LOGGER.error("Failed to turn off switch %s: %s", self._attr_unique_id, response.error_message)
        if isinstance(response, Success):
            _LOGGER.info("Successfully turned off switch %s", self._attr_unique_id)
        await self.coordinator.async_request_refresh()

    @property
    def is_on(self) -> bool | None:
        """Return the native value of the switch."""
        _LOGGER.debug(
            "Calling is_on for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        # Translate the value to a boolean
        value: Value | None = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            _LOGGER.error(
                "is_on for %s (%s) returned None",
                self.entity_description.key,
                self._attr_unique_id,
            )
            return None
        boolean_value = ETA_BINARY_SENSOR_VALUES_DE.get(str(value.value))
        if boolean_value is None:
            _LOGGER.error(
                "Unknown binary value %s for %s (%s)",
                value.value,
                self.entity_description.key,
                self._attr_unique_id,
            )
            return None
        return boolean_value
