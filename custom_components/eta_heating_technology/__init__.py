"""
Custom integration to integrate ETA heating technology with Home Assistant.

For more details about this integration, please refer to
https://github.com/Meraxa/home-assistant-eta-integration
"""

from __future__ import annotations
import re
from homeassistant.helpers.device_registry import DeviceInfo

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import EtaApiClient
from .const import CONF_HOST, CONF_PORT, DOMAIN, LOGGER
from .coordinator import EtaDataUpdateCoordinator
from .data import EtaData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import EtaConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    # Platform.BINARY_SENSOR,
    # Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: EtaConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = EtaDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=1),
    )
    entry.runtime_data = EtaData(
        client=EtaApiClient(
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    hass.data[DOMAIN][entry.entry_id] = hass_data
    hass.data[DOMAIN][entry.entry_id]["device_info"] = DeviceInfo(
        configuration_url=entry.data[CONF_HOST],
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="ETA Heiztechnik GmbH",
        name=f"IP: {entry.data[CONF_HOST]}",
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: EtaConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data: dict = hass.data[DOMAIN]
        data.pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: EtaConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
