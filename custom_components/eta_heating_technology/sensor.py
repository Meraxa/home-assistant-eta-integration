"""Sensor platform for eta_heating_technology."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)

from custom_components.eta_heating_technology.const import (
    CHOSEN_ENTITIES,
    DISCOVERED_ENTITIES,
    LOGGER,
)

from .entity import EtaEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.eta_heating_technology.api import EtaApiClient

    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


def determine_sensor_device_class(unit: str) -> SensorDeviceClass | None:
    """Determine the SensorDeviceClass of the sensor based on the unit string."""
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
        "m³/h": SensorDeviceClass.VOLUME_FLOW_RATE,
    }

    if unit in unit_dict_eta:
        return unit_dict_eta[unit]
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EtaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    sensor_keys: list[str] = config_entry.data[CHOSEN_ENTITIES]
    LOGGER.info("sensor_keys: %s", sensor_keys)

    eta_sensors: list[EtaSensor] = []
    for sensor_key in sensor_keys:
        sensor_url = config_entry.data[DISCOVERED_ENTITIES][sensor_key]["url"]
        sensor_name = config_entry.data[DISCOVERED_ENTITIES][sensor_key]["name"]

        api_client = config_entry.runtime_data.client
        sensor_unit = await api_client.async_get_value_unit(sensor_url)

        e = EtaSensor(
            coordinator=config_entry.runtime_data.coordinator,
            api_client=api_client,
            entity_description=SensorEntityDescription(
                key=sensor_key,
                name=sensor_name,
                device_class=determine_sensor_device_class(sensor_unit),
            ),
            config_entry_id=config_entry.entry_id,
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
        LOGGER.info(
            "Calling native_value for: %s with _attr_unique_id: %s",
            self.entity_description.key,
            self._attr_unique_id,
        )
        return self.coordinator.data.get(self.entity_description.key)
