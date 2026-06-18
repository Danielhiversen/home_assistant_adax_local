"""Support for Adax wifi-enabled home heaters."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from . import AdaxConfigEntry
from .coordinator import AdaxLocalCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdaxConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Adax thermostat with config flow."""
    async_add_entities([AdaxDevice(entry.runtime_data)])


class AdaxDevice(CoordinatorEntity[AdaxLocalCoordinator], ClimateEntity):
    """Representation of a heater."""

    _attr_hvac_mode = HVACMode.HEAT
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_icon = "mdi:radiator"
    _attr_max_temp = 35
    _attr_min_temp = 5
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: AdaxLocalCoordinator) -> None:
        """Initialize the heater."""
        super().__init__(coordinator)
        self._attr_unique_id = slugify(coordinator.adax.device_ip)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data["current_temperature"]

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data["target_temperature"]

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self.coordinator.adax.set_target_temperature(temperature)
        await self.coordinator.async_request_refresh()
