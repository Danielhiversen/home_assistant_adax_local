"""Support for Adax wifi-enabled home heaters."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_TOKEN,
    PRECISION_WHOLE,
    TEMP_CELSIUS,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import slugify

from .adax import Adax
from .const import DEVICE_IP

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Adax thermostat."""
    return True


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Adax thermostat with config flow."""
    adax_data_handler = Adax(
        entry.data[DEVICE_IP],
        entry.data[CONF_TOKEN],
        websession=async_get_clientsession(hass, verify_ssl=False),
    )
    async_add_entities([AdaxDevice(adax_data_handler)], True)


class AdaxDevice(ClimateEntity):
    """Representation of a heater."""

    def __init__(self, adax_data_handler):
        """Initialize the heater."""
        self._current_temperature = None
        self._set_temperature = None
        self._adax_data_handler = adax_data_handler
        self._available = False

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode."""
        return HVAC_MODE_HEAT

    @property
    def unique_id(self):
        """Return a unique ID."""
        return slugify(self._adax_data_handler.ip_address)

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def icon(self):
        """Return nice icon for heater."""
        return "mdi:radiator"

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_HEAT]

    @property
    def temperature_unit(self):
        """Return the unit of measurement which this device uses."""
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 5

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 35

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._set_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_WHOLE

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self._adax_data_handler.set_target_temperature(temperature)
        # await self._adax_data_handler.update(force_update=True)

    async def async_update(self):
        """Get the latest data."""
        (
            self._current_temperature,
            self._set_temperature,
        ) = await self._adax_data_handler.get_status()
        self._available = self._current_temperature is not None
