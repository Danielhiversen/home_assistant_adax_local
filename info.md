Local Integration for Adax heaters.

Custom component for using [Adax](https://adax.no/en/) heaters in Home Assistant with local access.
Requires an Adax heater with both wifi and Bluetooth. Bluetooth is only used for configuring the heater for local access.
Configure local access will remove the cloud access. Use https://github.com/Danielhiversen/home_assistant_adax/ for using the cloud API.

[Buy me a coffee :)](http://paypal.me/dahoiv)


{%- if selected_tag == "master" %}
## This is a development version!
This is **only** intended for test by developers!
{% endif %}

{%- if prerelease %}
## This is a beta version
Please be careful and do NOT install this on production systems. Also make sure to take a backup/snapshot before installing.
{% endif %}

# Features
- Support for Adax wifi heaters
- See temperature and set temperature
- Change set temperature and turn on/off

## Configuration
Go to integration page in HA, press + and search for Adax. Enter your Wifi ssid and Wifi password
