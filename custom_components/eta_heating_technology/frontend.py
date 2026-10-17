"""Serve the cockpit panel module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

_FRONTEND_FLAG = f"{DOMAIN}_frontend_registered"
FRONTEND_DIR = Path(__file__).parent / "frontend"


async def async_setup_frontend(hass: HomeAssistant) -> None:
    """Expose ``/<domain>/frontend`` once per Home Assistant process."""
    if hass.data.get(_FRONTEND_FLAG):
        return
    try:
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    f"/{DOMAIN}/frontend",
                    str(FRONTEND_DIR),
                    cache_headers=False,
                )
            ]
        )
    except RuntimeError as err:
        _LOGGER.warning("ETA cockpit assets were not published: %s", err)
        return
    hass.data[_FRONTEND_FLAG] = True
