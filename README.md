# Adax heaters
![Validate with hassfest](https://github.com/Danielhiversen/home_assistant_adax_local/workflows/Validate%20with%20hassfest/badge.svg)
[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Custom component for using [Adax](https://adax.no/en/) heaters in Home Assistant with local access.
Requires a newer Adax heater with both wifi and Bluetooth. Bluetooth is only used for configuring the heater for local access.
Configure local access will remove the cloud access. Use https://github.com/Danielhiversen/home_assistant_adax/ for using the cloud API.

[Support the developer](http://paypal.me/dahoiv)

## Install
Use [hacs](https://hacs.xyz/docs/faq/custom_repositories) or copy the files to the custom_components folder in Home Assistant config.

## Configuration
Go to integration page in HA, press + and search for Adax. Enter your Wifi ssid and Wifi password


[releases]: https://github.com/Danielhiversen/home_assistant_adax_local/releases
[releases-shield]: https://img.shields.io/github/release/Danielhiversen/home_assistant_adax_local.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/Danielhiversen/home_assistant_adax_local/total
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg
[hacs]: https://hacs.xyz/docs/default_repositories
