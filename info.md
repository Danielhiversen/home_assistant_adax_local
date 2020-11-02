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
- Support for all Adax wifi heaters
- See temperature and set temperature
- Change set temperature and turn on/off


## Configuration

1. Run setup_adax.py to configure your heater for local access

2. Go to integration page in HA, press + and search for Adax
   Enter your local ip
   Enter your token
