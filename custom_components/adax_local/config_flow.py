"""Adds config flow for Adax integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_TOKEN
from homeassistant.util import slugify

from .const import DEVICE_IP, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(DEVICE_IP): str, vol.Required(CONF_TOKEN): str})


async def validate_input(hass: core.HomeAssistant, device_ip):
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
                device_ip = user_input[DEVICE_IP].replace(" ", "")
                token = user_input[CONF_TOKEN].replace(" ", "")
                await validate_input(self.hass, device_ip)
                unique_id = slugify(device_ip)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=unique_id,
                    data={DEVICE_IP: device_ip, CONF_TOKEN: token},
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
