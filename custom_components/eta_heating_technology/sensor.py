"""Sensor platform for eta_heating_technology."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.eta_heating_technology.api import Object, Value
from custom_components.eta_heating_technology.const import (
    CHOSEN_ENTITIES,
    ETA_BINARY_SENSOR_VALUES_DE,
    ETA_SENSOR_UNITS,
    ETA_STRING_SENSOR_VALUES_DE,
    EtaSensorType,
)
from custom_components.eta_heating_technology.utils import determine_sensor_type

from .entity import EtaEntity

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.eta_heating_technology.api import EtaApiClient

    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


class ValueNoneError(Exception):
    """Exception indicating that a sensor value was `None`."""


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: EtaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    chosen_objects: list[Object] = [Object.model_validate(obj) for obj in config_entry.data[CHOSEN_ENTITIES]]
    _LOGGER.info("sensor_keys: %s", chosen_objects)

    eta_sensors: list[EtaSensor | EtaStringSensor] = []
    for obj in chosen_objects:
        api_client = config_entry.runtime_data.client
        value: Value = await api_client.async_get_data(obj.uri)
        sensor_type = determine_sensor_type(value)

        if sensor_type is EtaSensorType.SENSOR:
            e = EtaSensor(
                coordinator=config_entry.runtime_data.coordinator,
                api_client=api_client,
                entity_description=SensorEntityDescription(
                    key=obj.full_name,
                    name=obj.full_name,
                    device_class=ETA_SENSOR_UNITS[value.unit],
                    native_unit_of_measurement=value.unit,
                ),
                config_entry_id=config_entry.entry_id,
                url=obj.uri,
            )
        elif sensor_type is EtaSensorType.STRING_SENSOR:
            e = EtaStringSensor(
                coordinator=config_entry.runtime_data.coordinator,
                api_client=api_client,
                entity_description=SensorEntityDescription(
                    key=obj.full_name,
                    name=obj.full_name,
                ),
                config_entry_id=config_entry.entry_id,
                url=obj.uri,
            )
        if sensor_type is EtaSensorType.BINARY_SENSOR:
            continue
        if sensor_type is None:
            _LOGGER.error(
                "Unsupported sensor type for sensor: %s with uri: %s",
                obj.full_name,
                obj.uri,
            )
            continue
        eta_sensors.append(e)

    async_add_entities(eta_sensors)


class EtaSensor(EtaEntity, SensorEntity):
    """eta_heating_technology Sensor class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        api_client: EtaApiClient,
        config_entry_id: str,
        entity_description: SensorEntityDescription,
        url: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        # Add the config entry id to the unique id to avoid conflicts with
        # multiple eta installations
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self.url = url
        self.api_client = api_client
        self.coordinator = coordinator

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        _LOGGER.info(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        value: Value | None = self.coordinator.data.get(self.entity_description.key)
        if value is not None:
            return value.scaled_value
        msg = (
            f"Calling native_value for: {self.entity_description.key} with "
            f"_attr_unique_id: {self._attr_unique_id} failed because the returned "
            "value was `None`."
        )
        _LOGGER.error(msg=msg)
        return None


class EtaBinarySensor(EtaEntity, BinarySensorEntity):
    """eta_heating_technology BinarySensor class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        api_client: EtaApiClient,
        config_entry_id: str,
        entity_description: BinarySensorEntityDescription,
        url: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        # Add the config entry id to the unique id to avoid conflicts with
        # multiple eta installations
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self.url = url
        self.api_client = api_client
        self.coordinator = coordinator

    @property
    def is_on(self) -> bool | None:
        """Return the native value of the sensor."""
        _LOGGER.info(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        # Translate the value to a boolean
        value: Value | None = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            msg = (
                f"Calling native_value for: {self.entity_description.key} with "
                f"_attr_unique_id: {self._attr_unique_id} failed because the returned "
                "value was `None`."
            )
            _LOGGER.error(msg=msg)
            return None
        boolean_value = ETA_BINARY_SENSOR_VALUES_DE.get(str(value.value), None)
        if boolean_value is None:
            msg = (
                f"Calling native_value for: {self.entity_description.key} with "
                f"_attr_unique_id: {self._attr_unique_id} failed because the returned "
                f"value was {value}."
            )
            _LOGGER.error(msg=msg)
            return None
        return boolean_value


class EtaStringSensor(EtaEntity, SensorEntity):
    """eta_heating_technology Sensor class."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        api_client: EtaApiClient,
        config_entry_id: str,
        entity_description: SensorEntityDescription,
        url: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        # Add the config entry id to the unique id to avoid conflicts with
        # multiple eta installations
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self.url = url
        self.api_client = api_client
        self.coordinator = coordinator

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        _LOGGER.info(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        value: Value | None = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            msg = (
                f"Calling native_value for: {self.entity_description.key} with "
                f"_attr_unique_id: {self._attr_unique_id} failed because the returned "
                "value was `None`."
            )
            _LOGGER.error(msg=msg)
            return None
        string_value = ETA_STRING_SENSOR_VALUES_DE.get(str(value.value), None)
        if string_value is None:
            msg = (
                f"Calling native_value for: {self.entity_description.key} with "
                f"_attr_unique_id: {self._attr_unique_id} failed because the returned "
                f"value was {value}."
            )
            _LOGGER.error(msg=msg)
            return None
        return string_value
