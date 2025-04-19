"""Sensor platform for eta_heating_technology."""

from __future__ import annotations

from datetime import timedelta
from re import L
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.eta_heating_technology.api import EtaApiClient
from custom_components.eta_heating_technology.const import (
    CHOSEN_ENTITIES,
    DOMAIN,
    LOGGER,
    SENSORS_DICT,
)

from .entity import EtaEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


def determine_device_class(unit):
    unit_dict_eta = {
        "°C": SensorDeviceClass.TEMPERATURE,
        "W": SensorDeviceClass.POWER,
        "A": SensorDeviceClass.CURRENT,
        "Hz": SensorDeviceClass.FREQUENCY,
        "Pa": SensorDeviceClass.PRESSURE,
        "V": SensorDeviceClass.VOLTAGE,
        "W/m²": SensorDeviceClass.IRRADIANCE,
        "bar": SensorDeviceClass.PRESSURE,
        "kW": SensorDeviceClass.POWER,
        "kWh": SensorDeviceClass.ENERGY,
        "kg": SensorDeviceClass.WEIGHT,
        "mV": SensorDeviceClass.VOLTAGE,
        "s": SensorDeviceClass.DURATION,
        "%rH": SensorDeviceClass.HUMIDITY,
    }

    if unit in unit_dict_eta:
        return unit_dict_eta[unit]
    return None


def determine_precision(unit):
    """Determine the precision of the value based on the unit."""
    if unit in ["°C"]:
        return 1
    return 0


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: EtaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    config = hass.data[DOMAIN][entry.entry_id]
    LOGGER.info("Config entry data: %s", config)
    sensors: list[str] = config[CHOSEN_ENTITIES]
    LOGGER.info("Sensors: %s", sensors)

    eta_sensors: list[EtaSensor] = []
    for sensor in sensors:
        sensor_url = config[SENSORS_DICT][sensor]
        sensor_name = sensor
        sensor_key = sensor.lower().replace(" ", "_")

        # Add the sensor endpoint to the coordinator
        entry.runtime_data.coordinator.sensor_endpoints[sensor_key] = sensor_url

        api_client = entry.runtime_data.client
        sensor_unit = await api_client.async_get_value_unit(sensor_url)

        e = EtaSensor(
            coordinator=entry.runtime_data.coordinator,
            api_client=api_client,
            entity_description=SensorEntityDescription(
                key=sensor_key,
                name=sensor_name,
                device_class=determine_device_class(sensor_unit),
                native_unit_of_measurement=sensor_unit,
                suggested_display_precision=determine_precision(sensor_unit),
            ),
            config_entry_id=entry.entry_id,
            url=sensor_url,
        )
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
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self.url = url
        self.api_client = api_client

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        LOGGER.info("Calling native_value for: %s", self.entity_description.key)
        return self.coordinator.data.get(self.entity_description.key)
