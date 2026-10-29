"""Sensor platform for eta_heating_technology."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory

from .api import EtaApiClientError
from .const import (
    CHOSEN_BINARY_SENSORS,
    CHOSEN_SWITCHES,
    ETA_SENSOR_UNITS,
    ETA_STRING_SENSOR_VALUES_DE,
    ETA_UNIT_MAPPING,
    EtaSensorType,
)
from .entity import EtaEntity
from .utils import (
    determine_sensor_type,
    entity_data_key,
    entity_display_name,
    entity_unique_key,
)

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import Value
    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


async def async_setup_entry(  # noqa: PLR0912
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

    # None for entries created before switches were stored explicitly
    switch_names: list[str] | None = config_entry.data.get(CHOSEN_SWITCHES)
    binary_names: list[str] | None = config_entry.data.get(CHOSEN_BINARY_SENSORS)

    # Fetch initial values to determine types (use coordinator data if available)
    eta_sensors: list[EtaSensor | EtaStringSensor | EtaErrorsSensor] = [
        EtaErrorsSensor(coordinator=coordinator, config_entry_id=config_entry.entry_id),
    ]
    for obj in chosen_objects:
        if switch_names is not None and obj.full_name in switch_names:
            continue
        if binary_names is not None and obj.full_name in binary_names:
            continue
        data_key = entity_data_key(obj)
        unique_key = entity_unique_key(obj, chosen_objects)
        value = coordinator.data.get(data_key) if coordinator.data else None
        if value is None:
            try:
                value = await api_client.async_get_data(obj.uri)
            except EtaApiClientError as exception:
                _LOGGER.warning("Skipping sensor %s, no value available yet: %s", obj.full_name, exception)
                continue
        sensor_type = determine_sensor_type(value)
        if sensor_type is EtaSensorType.BINARY_SENSOR and switch_names is not None:
            # Legacy: on/off not stored as binary_sensor → text fallback
            sensor_type = EtaSensorType.STRING_SENSOR
        display_name = entity_display_name(obj, chosen_objects)

        if sensor_type is EtaSensorType.SENSOR:
            # Use TOTAL_INCREASING for cumulative energy sensors,
            # MEASUREMENT for instantaneous readings
            if value.unit == "kWh":
                state_class = SensorStateClass.TOTAL_INCREASING
            elif value.unit == "kg":
                state_class = SensorStateClass.TOTAL
            else:
                state_class = SensorStateClass.MEASUREMENT
            eta_sensors.append(
                EtaSensor(
                    coordinator=coordinator,
                    entity_description=SensorEntityDescription(
                        key=unique_key,
                        name=display_name,
                        device_class=ETA_SENSOR_UNITS.get(value.unit),
                        native_unit_of_measurement=ETA_UNIT_MAPPING.get(value.unit, value.unit),
                        state_class=state_class,
                    ),
                    config_entry_id=config_entry.entry_id,
                    data_key=data_key,
                )
            )
        elif sensor_type is EtaSensorType.STRING_SENSOR:
            eta_sensors.append(
                EtaStringSensor(
                    coordinator=coordinator,
                    entity_description=SensorEntityDescription(
                        key=unique_key,
                        name=display_name,
                    ),
                    config_entry_id=config_entry.entry_id,
                    data_key=data_key,
                )
            )
        elif sensor_type is EtaSensorType.BINARY_SENSOR:
            continue  # Handled by switch platform
        else:
            _LOGGER.warning(
                "Unsupported sensor type for sensor: %s with uri: %s (value=%r, unit=%r, str_value=%r)",
                obj.full_name,
                obj.uri,
                value.value,
                value.unit,
                value.str_value,
            )

    async_add_entities(eta_sensors)


class EtaSensor(EtaEntity, SensorEntity):
    """eta_heating_technology Sensor class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        config_entry_id: str,
        entity_description: SensorEntityDescription,
        data_key: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self._data_key = data_key

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        _LOGGER.debug(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        value: Value | None = self.coordinator.data.get(self._data_key)
        if value is not None:
            scaled = value.scaled_value
            # Ensure numeric sensors return float for HA statistics
            if isinstance(scaled, (int, float)):
                return scaled
            try:
                return float(scaled)
            except (ValueError, TypeError):
                # Numeric sensors must not report text, HA rejects that state
                _LOGGER.debug("Non-numeric value %r for %s", scaled, self.entity_description.key)
                return None
        _LOGGER.debug(
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
        data_key: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self._data_key = data_key

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        _LOGGER.debug(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        value: Value | None = self.coordinator.data.get(self._data_key)
        if value is None:
            _LOGGER.debug(
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
        # Last resort: return raw value as string
        return str(value.value)


class EtaErrorsSensor(EtaEntity, SensorEntity):
    """Number of active errors reported by `/user/errors`."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        config_entry_id: str,
    ) -> None:
        """Initialize the errors sensor."""
        super().__init__(coordinator)
        self.entity_description = SensorEntityDescription(
            key="active_errors",
            name="Active errors",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        self._attr_unique_id = f"{config_entry_id}-active_errors"

    @property
    def native_value(self) -> int:
        """Return the number of active errors."""
        return len(self.coordinator.active_errors)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return error details for automations and the UI."""
        return {
            "errors": self.coordinator.active_errors,
            "messages": [err.get("msg", "") for err in self.coordinator.active_errors],
        }
