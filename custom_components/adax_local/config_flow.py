"""Adds config flow for Adax integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_TOKEN
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import format_mac

from .adax import AdaxConfig, HeaterNotAvailable, HeaterNotFound, InvalidWifiCred
from .const import DEVICE_IP, DOMAIN

WIFI_SSID = "wifi_ssid"
WIFI_PSWD = "wifi_pswd"
_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(WIFI_SSID): str, vol.Required(WIFI_PSWD): str})


class AdaxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Adax integration."""

    VERSION = 1

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle a flow initialized by Bluetooth discovery."""
        await self.async_set_unique_id(format_mac(discovery_info.address))
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        return await self._async_provision(user_input, step_id="user")

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        return await self._async_provision(user_input, step_id="reconfigure")

    async def _async_provision(
        self, user_input: dict[str, Any] | None, step_id: str
    ) -> ConfigFlowResult:
        """Provision the heater over BLE and create or update the entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                configurator = AdaxConfig(
                    user_input[WIFI_SSID].strip(), user_input[WIFI_PSWD].strip()
                )
                if not await configurator.configure_device():
                    raise CannotConnect
            except CannotConnect:
                errors["base"] = "connection_error"
            except HeaterNotAvailable:
                return self.async_abort(reason="heater_not_available")
            except HeaterNotFound:
                return self.async_abort(reason="heater_not_found")
            except InvalidWifiCred:
                return self.async_abort(reason="invalid_wifi_cred")
            else:
                data = {
                    DEVICE_IP: configurator.device_ip,
                    CONF_TOKEN: configurator.access_token,
                }
                await self.async_set_unique_id(format_mac(configurator.mac_id))
                if step_id == "reconfigure":
                    self._abort_if_unique_id_mismatch(reason="wrong_heater")
                    return self.async_update_reload_and_abort(
                        self._get_reconfigure_entry(), data=data
                    )
                self._abort_if_unique_id_configured(updates=data)
                return self.async_create_entry(title=configurator.device_ip, data=data)

        return self.async_show_form(
            step_id=step_id,
            data_schema=DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
