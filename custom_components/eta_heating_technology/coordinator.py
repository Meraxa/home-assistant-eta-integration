"""DataUpdateCoordinator for eta_heating_technology."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CHOSEN_ENTITIES,
)

from .api import (
    EtaApiClientAuthenticationError,
    EtaApiClientError,
    Object,
    Value,
)

if TYPE_CHECKING:
    from .data import EtaConfigEntry

_LOGGER = logging.getLogger(__name__)


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EtaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EtaConfigEntry
    _cached_objects: list[Object] | None = None

    @property
    def chosen_objects(self) -> list[Object]:
        """Return parsed chosen objects, cached after first access."""
        if self._cached_objects is None:
            self._cached_objects = [
                Object.model_validate(obj)
                for obj in self.config_entry.data[CHOSEN_ENTITIES]
            ]
        return self._cached_objects

    def invalidate_cache(self) -> None:
        """Invalidate the cached objects (call after config entry data changes)."""
        self._cached_objects = None

    async def _async_update_data(self) -> dict[str, Value]:
        """Update data via library, fetching all entities concurrently."""
        try:
            _LOGGER.debug("Calling EtaDataUpdateCoordinator _async_update_data")
            objects = self.chosen_objects
            client = self.config_entry.runtime_data.client

            # Fetch all values concurrently instead of sequentially
            results = await asyncio.gather(
                *(client.async_get_data(obj.uri) for obj in objects),
                return_exceptions=True,
            )

            data: dict[str, Value] = {}
            for obj, result in zip(objects, results):
                if isinstance(result, EtaApiClientAuthenticationError):
                    raise ConfigEntryAuthFailed(result) from result
                if isinstance(result, Exception):
                    _LOGGER.warning(
                        "Failed to fetch data for %s: %s", obj.full_name, result
                    )
                    continue
                data[obj.full_name] = result

            return data
        except ConfigEntryAuthFailed:
            raise
        except EtaApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except EtaApiClientError as exception:
            raise UpdateFailed(exception) from exception
