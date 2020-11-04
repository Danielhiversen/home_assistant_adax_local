"""Adds config flow for Adax integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_TOKEN
from homeassistant.util import slugify

from .adax import AdaxConfig, HeaterNotAvailable, HeaterNotFound, InvalidWifiCred
from .const import DEVICE_IP, DOMAIN

WIFI_SSID = "wifi_ssid"
WIFI_PSWD = "wifi_pswd"
_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(WIFI_SSID): str, vol.Required(WIFI_PSWD): str})


def validate_input(hass: core.HomeAssistant, device_ip):
    """Validate the user input allows us to connect."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data[DEVICE_IP] == device_ip:
            raise AlreadyConfigured


class AdaxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Adax integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                wifi_ssid = user_input[WIFI_SSID].replace(" ", "")
                wifi_pswd = user_input[WIFI_PSWD].replace(" ", "")
                configurator = AdaxConfig(wifi_ssid, wifi_pswd)
                try:
                    success = await configurator.configure_device()
                except HeaterNotAvailable:
                    return self.async_abort(reason="heater_not_available")
                except HeaterNotFound:
                    return self.async_abort(reason="heater_not_found")
                except InvalidWifiCred:
                    return self.async_abort(reason="invalid_wifi_cred")
                if not success:
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

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class AlreadyConfigured(exceptions.HomeAssistantError):
    """Error to indicate host is already configured."""
