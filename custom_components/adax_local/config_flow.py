"""Adds config flow for Adax integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import core
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_TOKEN
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import slugify

from .adax import AdaxConfig, HeaterNotAvailable, HeaterNotFound, InvalidWifiCred
from .const import DEVICE_IP, DOMAIN

WIFI_SSID = "wifi_ssid"
WIFI_PSWD = "wifi_pswd"
_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(WIFI_SSID): str, vol.Required(WIFI_PSWD): str})


def validate_input(hass: core.HomeAssistant, device_ip: str) -> None:
    """Validate the user input allows us to connect."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data[DEVICE_IP] == device_ip:
            raise AlreadyConfigured


class AdaxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Adax integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                wifi_ssid = user_input[WIFI_SSID].replace(" ", "")
                wifi_pswd = user_input[WIFI_PSWD].replace(" ", "")
                configurator = AdaxConfig(wifi_ssid, wifi_pswd)
                if not await configurator.configure_device():
                    raise CannotConnect

                validate_input(self.hass, configurator.device_ip)
                unique_id = slugify(configurator.device_ip)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=unique_id,
                    data={
                        DEVICE_IP: configurator.device_ip,
                        CONF_TOKEN: configurator.access_token,
                    },
                )

            except AlreadyConfigured:
                return self.async_abort(reason="already_configured")
            except CannotConnect:
                errors["base"] = "connection_error"
            except HeaterNotAvailable:
                return self.async_abort(reason="heater_not_available")
            except HeaterNotFound:
                return self.async_abort(reason="heater_not_found")
            except InvalidWifiCred:
                return self.async_abort(reason="invalid_wifi_cred")

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class AlreadyConfigured(HomeAssistantError):
    """Error to indicate host is already configured."""
