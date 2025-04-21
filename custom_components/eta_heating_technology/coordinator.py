"""DataUpdateCoordinator for eta_heating_technology."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.eta_heating_technology.const import (
    CHOSEN_ENTITIES,
    DISCOVERED_ENTITIES,
)

from .api import (
    EtaApiClientAuthenticationError,
    EtaApiClientError,
)

if TYPE_CHECKING:
    from .data import EtaConfigEntry

_LOGGER = logging.getLogger(__name__)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EtaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EtaConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            _LOGGER.info("Calling EtaDataUpdateCoordinator _async_update_data")
            data = {}
            for sensor_key in self.config_entry.data[CHOSEN_ENTITIES]:
                sensor_url = self.config_entry.data[DISCOVERED_ENTITIES][sensor_key][
                    "url"
                ]
                (
                    value,
                    unit,
                ) = await self.config_entry.runtime_data.client.async_get_data(
                    sensor_url
                )
                data[sensor_key] = value
            return data
        except EtaApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except EtaApiClientError as exception:
            raise UpdateFailed(exception) from exception
