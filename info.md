Local integration for Adax heaters.

Custom component for controlling [Adax](https://adax.no/en/) wifi heaters in Home Assistant over your local network, with no dependency on the Adax cloud.

Requires a newer Adax heater with both wifi and Bluetooth. Bluetooth is used only once, during setup, to hand the heater your wifi credentials and an access token; all control afterwards happens over local polling.

Configuring local access removes the heater's cloud access. Use https://github.com/Danielhiversen/home_assistant_adax/ for the cloud API instead.

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
- Local control of Adax wifi heaters (no cloud)
- View current and target temperature
- Set the target temperature (5 – 35 °C)

## Configuration
Go to the integration page in Home Assistant, press **+**, and search for **Adax**. Reset the heater (hold **+** and **OK** for a few seconds), then hold **OK** until the blue LED blinks, and enter your wifi SSID and password.
