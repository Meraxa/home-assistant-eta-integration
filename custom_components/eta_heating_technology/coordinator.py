"""DataUpdateCoordinator for eta_heating_technology."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    EtaApiClientAuthenticationError,
    EtaApiClientError,
    Object,
    Value,
    normalize_object_uri,
)
from .const import (
    CHOSEN_ENTITIES,
)

if TYPE_CHECKING:
    from datetime import timedelta
    from logging import Logger

    from homeassistant.core import HomeAssistant

    from .data import EtaConfigEntry

_LOGGER = logging.getLogger(__name__)


def _varset_name(entry_id: str) -> str:
    """Build a short `[a-zA-Z0-9]+` variable set name from the config entry id."""
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", entry_id).lower()
    # Keep short — some ETA firmwares reject long set names with HTTP 400
    return f"ha{cleaned[-12:]}" or "haetasensors"


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EtaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EtaConfigEntry
    _cached_objects: list[Object] | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        name: str,
        update_interval: timedelta,
        config_entry: EtaConfigEntry,
    ) -> None:
        """Initialize coordinator state."""
        super().__init__(
            hass=hass,
            logger=logger,
            name=name,
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self.active_errors: list[dict[str, str]] = []
        self._varset_name = _varset_name(config_entry.entry_id)
        self._varset_uris: frozenset[str] | None = None

    @property
    def chosen_objects(self) -> list[Object]:
        """Return parsed chosen objects, cached after first access."""
        if self._cached_objects is None:
            self._cached_objects = [Object.model_validate(obj) for obj in self.config_entry.data[CHOSEN_ENTITIES]]
        return self._cached_objects

    def invalidate_cache(self) -> None:
        """Invalidate the cached objects (call after config entry data changes)."""
        self._cached_objects = None
        self._varset_uris = None

    async def _async_fetch_errors(self) -> None:
        """Refresh active ETA errors; failures are non-fatal for value polling."""
        client = self.config_entry.runtime_data.client
        try:
            errors = await client.async_get_errors()
            self.active_errors = errors.all_errors()
        except EtaApiClientError as exception:
            _LOGGER.debug("Could not fetch ETA errors: %s", exception)

    async def _async_fetch_via_varset(self, objects: list[Object]) -> dict[str, Value]:
        """Fetch all object values via a single `/user/vars` request."""
        client = self.config_entry.runtime_data.client
        uris = [obj.uri for obj in objects]
        uri_set = frozenset(normalize_object_uri(uri) for uri in uris)
        if self._varset_uris != uri_set:
            await client.async_ensure_varset(self._varset_name, uris)
            self._varset_uris = uri_set

        try:
            return await client.async_get_varset(self._varset_name)
        except EtaApiClientError:
            # Set lost after ETA reboot (or incomplete) — recreate once
            _LOGGER.info("Recreating ETA variable set %s", self._varset_name)
            self._varset_uris = None
            await client.async_ensure_varset(self._varset_name, uris)
            self._varset_uris = uri_set
            return await client.async_get_varset(self._varset_name)

    async def _async_fetch_individually(self, objects: list[Object]) -> dict[str, Value]:
        """Fallback: fetch each entity with limited concurrency."""
        client = self.config_entry.runtime_data.client
        sem = asyncio.Semaphore(3)

        async def _fetch(obj: Object) -> Value:
            async with sem:
                return await client.async_get_data(obj.uri)

        results = await asyncio.gather(
            *(_fetch(obj) for obj in objects),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, EtaApiClientAuthenticationError):
                raise ConfigEntryAuthFailed(result) from result
        if objects and not any(isinstance(result, Value) for result in results):
            msg = f"No values received from the ETA device: {results[0]}"
            raise UpdateFailed(msg)

        data: dict[str, Value] = {}
        if self.data:
            data.update(self.data)
        for obj, result in zip(objects, results, strict=False):
            if isinstance(result, Exception):
                _LOGGER.warning(
                    "Failed to fetch data for %s (%s): %s",
                    obj.full_name,
                    obj.uri,
                    result,
                )
                continue
            if isinstance(result, Value):
                data[obj.uri] = result
        return data

    async def _async_update_data(self) -> dict[str, Value]:
        """Update data via variable set, with per-entity fallback."""
        try:
            _LOGGER.debug("Calling EtaDataUpdateCoordinator _async_update_data")
            objects = self.chosen_objects
            await self._async_fetch_errors()

            if not objects:
                return self.data or {}

            try:
                bulk = await self._async_fetch_via_varset(objects)
                data: dict[str, Value] = {}
                if self.data:
                    data.update(self.data)
                for obj in objects:
                    key = normalize_object_uri(obj.uri)
                    if key in bulk:
                        data[obj.uri] = bulk[key]
                    else:
                        _LOGGER.warning("Variable set missing value for %s (%s)", obj.full_name, obj.uri)
                if any(obj.uri in data for obj in objects):
                    return data
                msg = "Variable set returned no matching values"
                raise EtaApiClientError(msg)  # noqa: TRY301
            except EtaApiClientAuthenticationError:
                raise
            except EtaApiClientError as exception:
                _LOGGER.warning("Bulk varset fetch failed, falling back to individual requests: %s", exception)
                return await self._async_fetch_individually(objects)
        except ConfigEntryAuthFailed:
            raise
        except EtaApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except EtaApiClientError as exception:
            raise UpdateFailed(exception) from exception
