# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Home Assistant custom integration** (HACS) for controlling Adax wifi heaters over the **local network** instead of the Adax cloud API. It targets newer Adax heaters that have both wifi and Bluetooth. Bluetooth (BLE) is used *only once*, during setup, to push wifi credentials and a self-generated access token onto the heater; all subsequent control happens over local HTTPS. Enabling local access disables the heater's cloud access (and vice versa — the cloud version is a separate integration: `home_assistant_adax`).

All code lives under `custom_components/adax_local/`. There is no build step, package manager, or test suite in this repo — it is deployed by copying the folder into a Home Assistant `config/custom_components/` directory (or installing via HACS).

## Architecture

The integration follows the standard Home Assistant config-flow + platform layout. The key flow to understand spans several files:

- **`adax.py`** — the only file with real domain logic; has no Home Assistant dependencies (pure `aiohttp`/`bleak`). Two classes:
  - `AdaxConfig` — **one-time BLE provisioning** (via `bleak.BleakScanner.discover(..., return_adv=True)`). Scans for an unregistered Adax heater (`scan_for_available_ble_device` / `device_available` parse the advertisement's `service_uuids` and `manufacturer_data`; device type `ADAX_DEVICE_TYPE_HEATER_BLE ∈ {5, 11, 17}`, must be not-registered and not-managed). It connects via `bleak_retry_connector.establish_connection` with a plain `bleak.BleakClient` (fresh service discovery — avoids a stale GATT cache on re-paired heaters), then writes a `command=join&ssid=...&psk=...&token=...` payload over a GATT characteristic, chunked into 17-byte frames by `write_command`. The heater replies via `notification_handler` with a status byte and its assigned IP. The `access_token` is a locally generated `secrets.token_hex(10)` — *the heater learns the token from us*, it is not retrieved from Adax.
  - `Adax` — **runtime control over HTTPS**. Talks to `https://<device_ip>/api` with `Authorization: Basic <token>`. `get_status` (`command=stat`) and `set_target_temperature` (`command=set_target`). Note the API uses temperatures in **centidegrees** (value × 100), so all conversions multiply/divide by 100.
- **`config_flow.py`** — UI setup. Collects wifi SSID/password, drives `AdaxConfig.configure_device()`, and stores `{device_ip, token}` in the config entry. The entry `unique_id` is the heater's BLE MAC (`format_mac`). Three entry points: `async_step_user` (manual), `async_step_bluetooth` (auto-discovery via the `bluetooth` matcher in `manifest.json`), and `async_step_reconfigure` (re-pair in place, guarded by `_abort_if_unique_id_mismatch`). Maps `adax.py` exceptions (`HeaterNotFound`, `HeaterNotAvailable`, `InvalidWifiCred`, `CannotConnect`) to abort/error reasons.
- **`__init__.py`** — creates the `Adax` client (session with `verify_ssl=False`) and an `AdaxLocalCoordinator`, runs `async_config_entry_first_refresh()`, stores the coordinator on `entry.runtime_data` (typed `AdaxConfigEntry`), and forwards to the `climate` platform.
- **`coordinator.py`** — `AdaxLocalCoordinator(DataUpdateCoordinator)` polls `Adax.get_status` every 60s, returns `{current_temperature, target_temperature}`, and raises `UpdateFailed` when the heater returns no data (this drives entity availability).
- **`climate.py`** — exposes `AdaxDevice(CoordinatorEntity, ClimateEntity)` using the `_attr_*` + enum API (`HVACMode.HEAT`, `ClimateEntityFeature.TARGET_TEMPERATURE`, `UnitOfTemperature.CELSIUS`). Reads temperatures from `coordinator.data`; `async_set_temperature` writes via `Adax.set_target_temperature` then requests a coordinator refresh. Single HVAC mode (`HEAT`), 5–35 °C, whole-degree steps. The entity `unique_id` stays `slugify(device_ip)`.

The integration is **local polling** — no push from the device; the coordinator polls on its own 60s interval.

## Important conventions

- **Self-signed TLS**: the runtime HTTPS session must use `verify_ssl=False` (set in `__init__.py`). Do not "fix" this to verify certs — the heater has no valid cert.
- **Temperatures are ×100** on the wire (`targTemp`/`currTemp` and `set_target`'s `value`).
- **Token direction**: the access token is generated on our side and pushed to the heater, not fetched. This is the inverse of cloud integrations.
- `const.py` holds `DOMAIN = "adax_local"` and the `DEVICE_IP` key; `manifest.json` requires `bleak` + `bleak-retry-connector` and depends on the `bluetooth` component (for discovery).

## Commands / CI

There is no test/build harness; the checks are formatting, linting, and Home Assistant manifest/structure validation.

- **Bootstrap**: `./scripts/setup` — creates `venv/`, installs `requirements-dev.txt`, and runs `pre-commit install`.
- **Run all checks**: `pre-commit run --all-files` (black + flake8 + basic file hooks).
- **Formatting**: `black .` (CI checks with `--check`, pinned to the version in `.pre-commit-config.yaml` / `lint.yaml`; it does not auto-fix).
- **Linting**: `flake8 .` (config in `.flake8`: line length 120, `E203`/`W503` ignored for black compatibility).
- **HA validation**: `hassfest` (via `home-assistant/actions/hassfest`) and HACS validation (`hacs/integration/action`) run in CI.

`pre-commit` runs black/flake8 on every commit. Keep the pinned versions in `.pre-commit-config.yaml`, `requirements-dev.txt`, and `lint.yaml` in sync. Bump `version` in `manifest.json` for releases.
