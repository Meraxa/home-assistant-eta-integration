"""DataUpdateCoordinator for eta_heating_technology."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.eta_heating_technology.const import DOMAIN, LOGGER

from .api import (
    EtaApiClientAuthenticationError,
    EtaApiClientError,
)

if TYPE_CHECKING:
    from .data import EtaConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EtaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EtaConfigEntry
    sensor_endpoints: dict[str, str] = {}

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            LOGGER.info("Calling EtaDataUpdateCoordinator _async_update_data")
            data = {}
            for sensor_key, endpoint in self.sensor_endpoints.items():
                (
                    value,
                    unit,
                ) = await self.config_entry.runtime_data.client.async_get_data(endpoint)
                data[sensor_key] = value
            return data
        except EtaApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except EtaApiClientError as exception:
            raise UpdateFailed(exception) from exception
