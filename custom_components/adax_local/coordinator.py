"""DataUpdateCoordinator for the Adax local integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .adax import Adax
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class AdaxLocalCoordinator(DataUpdateCoordinator[dict[str, float | None]]):
    """Coordinator that polls a single Adax heater over the local API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, adax: Adax) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {adax.device_ip}",
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
        )
        self.adax = adax

    async def _async_update_data(self) -> dict[str, float | None]:
        """Fetch the latest status from the heater."""
        current_temperature, target_temperature = await self.adax.get_status()
        if current_temperature is None:
            raise UpdateFailed("No data received from heater")
        return {
            "current_temperature": current_temperature,
            "target_temperature": target_temperature,
        }
