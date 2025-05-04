"""
Custom integration to integrate ETA heating technology with Home Assistant.

For more details about this integration, please refer to
https://github.com/Meraxa/home-assistant-eta-integration
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import EtaApiClient
from .const import CONF_HOST, CONF_PORT, DOMAIN, LOGGER
from .coordinator import EtaDataUpdateCoordinator
from .data import EtaData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import EtaConfigEntry

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: EtaConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = EtaDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=1),
        config_entry=config_entry,
    )
    config_entry.runtime_data = EtaData(
        client=EtaApiClient(
            host=config_entry.data[CONF_HOST],
            port=config_entry.data[CONF_PORT],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, config_entry.domain),
        coordinator=coordinator,
    )

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        manufacturer="Eta Heating Technology",
        name="Eta Heating System",
    )

    _LOGGER.info("Config entry data keys: %s", config_entry.data.keys())

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    # Forward the Config Entry set up to the platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    config_entry: EtaConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        _LOGGER.info("Unloading of config entry %s successful.", config_entry.entry_id)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    config_entry: EtaConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, config_entry)
    await async_setup_entry(hass, config_entry)
