"""Custom types for eta_heating_technology."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import EtaApiClient
    from .coordinator import EtaDataUpdateCoordinator


type EtaConfigEntry = ConfigEntry[EtaData]


@dataclass
class EtaData:
    """Data for the eta_heating_technology integration."""

    client: EtaApiClient
    coordinator: EtaDataUpdateCoordinator
