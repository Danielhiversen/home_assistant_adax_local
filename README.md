# Adax heaters
![Validate with hassfest](https://github.com/Danielhiversen/home_assistant_adax_local/workflows/Validate%20with%20hassfest/badge.svg)
[![GitHub Release][releases-shield]][releases]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Custom component for using [Adax](https://adax.no/en/) heaters in Home Assistant with local access.

Configure local access will remove the cloud access. Use https://github.com/Danielhiversen/home_assistant_adax/ for using the cloud API.

[Support the developer](http://paypal.me/dahoiv)


## Install
Use [hacs](https://hacs.xyz/docs/faq/custom_repositories) or copy the files to the custom_components folder in Home Assistant config.

## Configuration

1. Install the dependency `pip install bleak`

2. Run `python adax_config.py YOUR_WIFI_SSID YOUR_WIFI_PASSWORD` to configure your heater for local access. You do not need to run the script from the same computer as Home Assistant is running. The the heater and computer should not be to far away when the script is running.

2. Go to integration page in HA, press + and search for Adax
   Enter your local ip
   Enter your token


[releases]: https://github.com/Danielhiversen/home_assistant_adax_local/releases
[releases-shield]: https://img.shields.io/github/release/Danielhiversen/home_assistant_adax_local.svg?style=popout
[downloads-total-shield]: https://img.shields.io/github/downloads/Danielhiversen/home_assistant_adax_local/total
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg
[hacs]: https://hacs.xyz/docs/default_repositories
