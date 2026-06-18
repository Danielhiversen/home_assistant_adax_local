# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Home Assistant custom integration** (HACS) for controlling Adax wifi heaters over the **local network** instead of the Adax cloud API. It targets newer Adax heaters that have both wifi and Bluetooth. Bluetooth (BLE) is used *only once*, during setup, to push wifi credentials and a self-generated access token onto the heater; all subsequent control happens over local HTTPS. Enabling local access disables the heater's cloud access (and vice versa — the cloud version is a separate integration: `home_assistant_adax`).

All code lives under `custom_components/adax_local/`. There is no build step, package manager, or test suite in this repo — it is deployed by copying the folder into a Home Assistant `config/custom_components/` directory (or installing via HACS).

## Architecture

The integration follows the standard Home Assistant config-flow + platform layout. The key flow to understand spans several files:

- **`adax.py`** — the only file with real domain logic; has no Home Assistant dependencies (pure `aiohttp`/`bleak`). Two classes:
  - `AdaxConfig` — **one-time BLE provisioning** (via `bleak.BleakScanner.discover(..., return_adv=True)`). Scans for an unregistered Adax heater (`scan_for_available_ble_device` / `device_available` parse the advertisement's `service_uuids` and `manufacturer_data`; device type `ADAX_DEVICE_TYPE_HEATER_BLE = 5`, must be not-registered and not-managed). It then writes a `command=join&ssid=...&psk=...&token=...` payload over a GATT characteristic, chunked into 17-byte frames by `write_command`. The heater replies via `notification_handler` with a status byte and its assigned IP. The `access_token` is a locally generated `secrets.token_hex(10)` — *the heater learns the token from us*, it is not retrieved from Adax.
  - `Adax` — **runtime control over HTTPS**. Talks to `https://<device_ip>/api` with `Authorization: Basic <token>`. `get_status` (`command=stat`) and `set_target_temperature` (`command=set_target`). Note the API uses temperatures in **centidegrees** (value × 100), so all conversions multiply/divide by 100.
- **`config_flow.py`** — UI setup. Collects wifi SSID/password, drives `AdaxConfig.configure_device()`, and on success stores `{device_ip, token}` in the config entry. Uniqueness is keyed on `slugify(device_ip)`. Maps the custom exceptions from `adax.py` (`HeaterNotFound`, `HeaterNotAvailable`, `InvalidWifiCred`, `CannotConnect`, `AlreadyConfigured`) to abort/error reasons.
- **`__init__.py`** — forwards the config entry to the `climate` platform (setup/unload only).
- **`climate.py`** — exposes `AdaxDevice(ClimateEntity)` using the modern `_attr_*` + enum API (`HVACMode.HEAT`, `ClimateEntityFeature.TARGET_TEMPERATURE`, `UnitOfTemperature.CELSIUS`). Single HVAC mode (`HEAT`), target-temperature support only, range 5–35 °C, whole-degree steps. `async_update` polls `Adax.get_status`; availability is driven by whether a current temperature was returned. The client session is created with `verify_ssl=False` because the heater serves a self-signed cert.

The integration is **local polling** — no push from the device; Home Assistant calls `async_update` on its own cadence.

## Important conventions

- **Self-signed TLS**: the runtime HTTPS session must use `verify_ssl=False` (set in `climate.py`). Do not "fix" this to verify certs — the heater has no valid cert.
- **Temperatures are ×100** on the wire (`targTemp`/`currTemp` and `set_target`'s `value`).
- **Token direction**: the access token is generated on our side and pushed to the heater, not fetched. This is the inverse of cloud integrations.
- `const.py` holds `DOMAIN = "adax_local"` and the `DEVICE_IP` key; `manifest.json` declares the only Python dependency, `bleak`.

## Commands / CI

There is no test/build harness; the checks are formatting, linting, and Home Assistant manifest/structure validation.

- **Bootstrap**: `./scripts/setup` — creates `venv/`, installs `requirements-dev.txt`, and runs `pre-commit install`.
- **Run all checks**: `pre-commit run --all-files` (black + flake8 + basic file hooks).
- **Formatting**: `black .` (CI checks with `--check`, pinned to the version in `.pre-commit-config.yaml` / `lint.yaml`; it does not auto-fix).
- **Linting**: `flake8 .` (config in `.flake8`: line length 120, `E203`/`W503` ignored for black compatibility).
- **HA validation**: `hassfest` (via `home-assistant/actions/hassfest`) and HACS validation (`hacs/integration/action`) run in CI.

`pre-commit` runs black/flake8 on every commit. Keep the pinned versions in `.pre-commit-config.yaml`, `requirements-dev.txt`, and `lint.yaml` in sync. Bump `version` in `manifest.json` for releases.
