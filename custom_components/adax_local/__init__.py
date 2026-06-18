"""The Adax heater integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .adax import Adax
from .const import DEVICE_IP
from .coordinator import AdaxLocalCoordinator

PLATFORMS = [Platform.CLIMATE]

type AdaxConfigEntry = ConfigEntry[AdaxLocalCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AdaxConfigEntry) -> bool:
    """Set up the Adax heater."""
    adax = Adax(
        entry.data[DEVICE_IP],
        entry.data[CONF_TOKEN],
        websession=async_get_clientsession(hass, verify_ssl=False),
    )
    coordinator = AdaxLocalCoordinator(hass, entry, adax)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AdaxConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
