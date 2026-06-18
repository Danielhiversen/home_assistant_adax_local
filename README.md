# Adax heaters (local)
![Validate with hassfest](https://github.com/Danielhiversen/home_assistant_adax_local/workflows/Validate%20with%20hassfest/badge.svg)
[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant custom component for controlling [Adax](https://adax.no/en/) wifi heaters over your **local network**, with no dependency on the Adax cloud.

[Support the developer](http://paypal.me/dahoiv)

## How it works

This integration talks to the heater directly on your LAN over HTTPS. Bluetooth (BLE) is used **only once**, during setup, to hand the heater your wifi credentials plus a locally generated access token; all temperature reads and writes afterwards happen over local HTTP polling.

- **Setup (one time, BLE):** Home Assistant scans for the heater over Bluetooth, sends it your wifi SSID/password and an access token, and the heater reports back the IP address it received on your wifi.
- **Runtime (local HTTPS):** Home Assistant polls `https://<heater-ip>/api` using that token to read the current/target temperature and to set a new target.

> ⚠️ **Local access and cloud access are mutually exclusive.** Configuring a heater for local access **removes its cloud access**. If you want to use the Adax cloud API instead, use [home_assistant_adax](https://github.com/Danielhiversen/home_assistant_adax/) (re-pair the heater in the Adax app to switch back).

## Requirements

- A **newer Adax heater with both wifi and Bluetooth**. Bluetooth-only or wifi-only models are not supported. (BLE heater types `5`, `11` and `17` are recognised.)
- A Home Assistant host with a **Bluetooth adapter that can reach the heater** during setup (the heater needs to be physically close to the HA machine while pairing).
- The heater and Home Assistant on the **same local network** for ongoing control.

## Installation

### HACS (recommended)
1. In HACS, add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) (category: *Integration*).
2. Search for **Adax Local**, install it.
3. Restart Home Assistant.

### Manual
1. Copy `custom_components/adax_local` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

The integration is set up entirely from the UI — no YAML.

1. Go to **Settings → Devices & Services → + Add Integration** and search for **Adax** (pick the *local* one).
2. **Reset the heater**: press and hold **+** and **OK** together for a few seconds.
3. Press and hold the **OK** button until the **blue LED starts blinking**.
4. Enter your **wifi SSID** and **wifi password**, then submit.

Configuring the heater can take a few minutes. Keep the heater close to the Home Assistant machine during this step.

Each heater is added as a single `climate` entity:

| Capability | Value |
| --- | --- |
| HVAC mode | Heat |
| Temperature range | 5 – 35 °C |
| Step | 1 °C |
| Reports | Current temperature, target temperature |

## Troubleshooting

| Message | Meaning / fix |
| --- | --- |
| **Heater not found** | The heater wasn't discovered over Bluetooth. Move it closer to the Home Assistant machine and retry. |
| **Heater not available** | The heater isn't in a pairable state. Reset it (hold **+** and **OK** for a few seconds) and try again. |
| **Connection failed** | Pairing started but didn't complete. Move the heater closer and make sure the **blue LED is blinking** before submitting. |
| **Wifi credentials are invalid** | The SSID/password were rejected by the heater. Double-check them (note: spaces are stripped from both fields). |
| **The heater is already configured** | This heater (by its assigned IP) is already added in Home Assistant. |

If the heater changes IP address on your network, re-adding it may be required; assigning it a static/reserved IP in your router is recommended.

## Credits

The device communication is based on [pyAdaxLocal](https://github.com/Danielhiversen/pyAdaxLocal). Maintained by [@Danielhiversen](https://github.com/Danielhiversen).

[releases]: https://github.com/Danielhiversen/home_assistant_adax_local/releases
[releases-shield]: https://img.shields.io/github/release/Danielhiversen/home_assistant_adax_local.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/Danielhiversen/home_assistant_adax_local/total
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg
[hacs]: https://hacs.xyz/docs/default_repositories
