"""Support for Adax wifi-enabled home heaters."""
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_TOKEN,
    PRECISION_WHOLE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .adax import Adax
from .const import DEVICE_IP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Adax thermostat with config flow."""
    adax_data_handler = Adax(
        entry.data[DEVICE_IP],
        entry.data[CONF_TOKEN],
        websession=async_get_clientsession(hass, verify_ssl=False),
    )
    async_add_entities([AdaxDevice(adax_data_handler)], True)


class AdaxDevice(ClimateEntity):
    """Representation of a heater."""

    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_icon = "mdi:radiator"
    _attr_max_temp = 35
    _attr_min_temp = 5
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, adax_data_handler: Adax) -> None:
        """Initialize the heater."""
        self._adax_data_handler = adax_data_handler
        self._attr_unique_id = slugify(adax_data_handler.device_ip)
        self._attr_available = False

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self._adax_data_handler.set_target_temperature(temperature)

    async def async_update(self) -> None:
        """Get the latest data."""
        (
            self._attr_current_temperature,
            self._attr_target_temperature,
        ) = await self._adax_data_handler.get_status()
        self._attr_available = self._attr_current_temperature is not None
