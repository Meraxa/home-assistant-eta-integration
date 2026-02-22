"""Sensor platform for eta_heating_technology."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .api import Value
from .const import (
    ETA_SENSOR_UNITS,
    ETA_STRING_SENSOR_VALUES_DE,
    EtaSensorType,
)
from .utils import determine_sensor_type
from .entity import EtaEntity

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: EtaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = config_entry.runtime_data.coordinator
    api_client = config_entry.runtime_data.client

    # Use coordinator's cached objects to avoid re-parsing every time
    chosen_objects = coordinator.chosen_objects
    _LOGGER.debug("sensor_keys: %s", chosen_objects)

    # Fetch initial values to determine types (use coordinator data if available)
    eta_sensors: list[EtaSensor | EtaStringSensor] = []
    for obj in chosen_objects:
        if coordinator.data and obj.full_name in coordinator.data:
            value = coordinator.data[obj.full_name]
        else:
            value = await api_client.async_get_data(obj.uri)
        sensor_type = determine_sensor_type(value)

        if sensor_type is EtaSensorType.SENSOR:
            eta_sensors.append(
                EtaSensor(
                    coordinator=coordinator,
                    entity_description=SensorEntityDescription(
                        key=obj.full_name,
                        name=obj.full_name,
                        device_class=ETA_SENSOR_UNITS.get(value.unit),
                        native_unit_of_measurement=value.unit,
                        state_class=SensorStateClass.MEASUREMENT,
                    ),
                    config_entry_id=config_entry.entry_id,
                )
            )
        elif sensor_type is EtaSensorType.STRING_SENSOR:
            eta_sensors.append(
                EtaStringSensor(
                    coordinator=coordinator,
                    entity_description=SensorEntityDescription(
                        key=obj.full_name,
                        name=obj.full_name,
                    ),
                    config_entry_id=config_entry.entry_id,
                )
            )
        elif sensor_type is EtaSensorType.BINARY_SENSOR:
            continue  # Handled by switch platform
        else:
            _LOGGER.warning(
                "Unsupported sensor type for sensor: %s with uri: %s",
                obj.full_name,
                obj.uri,
            )

    async_add_entities(eta_sensors)


class EtaSensor(EtaEntity, SensorEntity):
    """eta_heating_technology Sensor class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        config_entry_id: str,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        _LOGGER.debug(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        value: Value | None = self.coordinator.data.get(self.entity_description.key)
        if value is not None:
            return value.scaled_value
        _LOGGER.error(
            "native_value for %s (%s) returned None",
            self.entity_description.key,
            self._attr_unique_id,
        )
        return None


class EtaStringSensor(EtaEntity, SensorEntity):
    """eta_heating_technology String Sensor class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        config_entry_id: str,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        _LOGGER.debug(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        value: Value | None = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            _LOGGER.error(
                "native_value for %s (%s) returned None",
                self.entity_description.key,
                self._attr_unique_id,
            )
            return None
        string_value = ETA_STRING_SENSOR_VALUES_DE.get(str(value.value))
        if string_value is not None:
            return string_value
        # Fallback: use strValue directly from the ETA API response
        # This supports all state code ranges (2000, 4000, etc.)
        if value.str_value:
            return value.str_value
        _LOGGER.warning(
            "No string mapping and no strValue for value %s of %s (%s)",
            value.value,
            self.entity_description.key,
            self._attr_unique_id,
        )
        return None
