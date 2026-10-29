"""Register the ETA cockpit as a sidebar panel."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .cockpit import entity_path
from .const import CONF_HOST, CONF_PORT, DOMAIN, VERSION

_LOGGER = logging.getLogger(__name__)

PANEL_URL_PATH = "eta-cockpit"
PANEL_COMPONENT = "eta-heating-panel"
_PANEL_MODULE = f"/{DOMAIN}/frontend/panel/eta-panel.js"
_PANEL_FLAG = f"{DOMAIN}_panel_registered"
_WS_FLAG = f"{DOMAIN}_panel_ws_registered"
WS_PANEL_ENTITIES = f"{DOMAIN}/panel_entities"

_LOGGER_SETUP = "ETA cockpit panel was not registered: %s"


def panel_module_url() -> str:
    """Return the panel module URL, cache-busted with the integration version."""
    return f"{_PANEL_MODULE}?v={VERSION}"


def _loaded_entries(hass: HomeAssistant) -> list[Any]:
    return [entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.state is ConfigEntryState.LOADED]


def panel_entities(hass: HomeAssistant) -> dict[str, Any]:
    """
    Resolve every entity of each loaded ETA config entry.

    The panel addresses entities by registry id, so a renamed entity_id keeps
    working. Disabled entities stay in the list and are marked.
    """
    entries = _loaded_entries(hass)
    if not entries:
        return {"entries": []}
    registry = er.async_get(hass)
    payload: list[dict[str, Any]] = []
    for entry in entries:
        entities = [
            {
                "entity_id": reg_entry.entity_id,
                "domain": reg_entry.domain,
                "path": entity_path(entry.entry_id, reg_entry.unique_id or ""),
                "disabled": reg_entry.disabled_by is not None,
            }
            for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id)
        ]
        entities.sort(key=lambda item: (item["path"], item["entity_id"]))
        payload.append(
            {
                "entry_id": entry.entry_id,
                "host": entry.data.get(CONF_HOST),
                "port": entry.data.get(CONF_PORT),
                "entities": entities,
            }
        )
    return {"entries": payload}


@websocket_api.websocket_command({vol.Required("type"): WS_PANEL_ENTITIES})
@callback
def _ws_panel_entities(hass: HomeAssistant, connection: Any, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], panel_entities(hass))


async def async_register_panel(hass: HomeAssistant) -> None:
    """
    Add the ETA panel to the sidebar once, for every user.

    A failure here must not abort integration setup.
    """
    if not hass.data.get(_WS_FLAG):
        websocket_api.async_register_command(hass, _ws_panel_entities)
        hass.data[_WS_FLAG] = True
    if hass.data.get(_PANEL_FLAG):
        return
    try:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL_PATH,
            webcomponent_name=PANEL_COMPONENT,
            sidebar_title="ETA",
            sidebar_icon="mdi:radiator",
            module_url=panel_module_url(),
            require_admin=False,
        )
    except ValueError as err:
        _LOGGER.warning(_LOGGER_SETUP, err)
        return
    hass.data[_PANEL_FLAG] = True


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the panel from the sidebar."""
    if hass.data.pop(_PANEL_FLAG, False):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
