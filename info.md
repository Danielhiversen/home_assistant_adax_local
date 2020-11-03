Local Integration for Adax heaters

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

1. Install the dependency `pip install bleak`

2. Run `python adax_config.py YOUR_WIFI_SSID YOUR_WIFI_PASSWORD` to configure your heater for local access. You do not need to run the script from the same computer as Home Assistant is running. The heater and the computer should not be to far away when the script is running.

2. Go to integration page in HA, press + and search for Adax
   Enter your local ip
   Enter your token
