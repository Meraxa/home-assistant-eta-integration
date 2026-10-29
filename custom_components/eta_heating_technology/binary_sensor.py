"""Binary sensor platform for eta_heating_technology."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import (
    CHOSEN_BINARY_SENSORS,
    ETA_BINARY_SENSOR_VALUES_DE,
)
from .entity import EtaEntity
from .utils import (
    entity_data_key,
    entity_display_name,
    entity_unique_key,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import Value
    from .coordinator import EtaDataUpdateCoordinator
    from .data import EtaConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: EtaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = config_entry.runtime_data.coordinator
    chosen_objects = coordinator.chosen_objects

    # Absent on legacy entries — those keep treating binaries as switches
    binary_names: list[str] | None = config_entry.data.get(CHOSEN_BINARY_SENSORS)
    if binary_names is None:
        async_add_entities([])
        return

    entities = [
        EtaBinarySensor(
            coordinator=coordinator,
            entity_description=BinarySensorEntityDescription(
                key=entity_unique_key(obj, chosen_objects),
                name=entity_display_name(obj, chosen_objects),
            ),
            config_entry_id=config_entry.entry_id,
            data_key=entity_data_key(obj),
        )
        for obj in chosen_objects
        if obj.full_name in binary_names
    ]
    async_add_entities(entities)


class EtaBinarySensor(EtaEntity, BinarySensorEntity):
    """Read-only on/off ETA endpoint."""

    def __init__(
        self,
        coordinator: EtaDataUpdateCoordinator,
        config_entry_id: str,
        entity_description: BinarySensorEntityDescription,
        data_key: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry_id}-{entity_description.key}"
        self.entity_description = entity_description
        self._data_key = data_key

    @property
    def is_on(self) -> bool | None:
        """Return True when the ETA value is on."""
        value: Value | None = self.coordinator.data.get(self._data_key)
        if value is None:
            return None
        return ETA_BINARY_SENSOR_VALUES_DE.get(str(value.value))
