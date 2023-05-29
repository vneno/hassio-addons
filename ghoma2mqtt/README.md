# ghoma2mqtt

## About

G-Homa smart plugs bridge to MQTT server with auto discovery feature

Energy monitoring feature is _NOT_ implemented

Utility to configure your G-Homa plugs: 
```
plug_configure.py
```

## Prepare G-Homa smart plug
Reset the Plug and enable AP:
- press and hold down the power button for ~7s (LED blinks fast), release the button
- pres and hold the power button for ~4s (LED blinks intermittently 4x short blinks), release the button


Configure the Plug:
- connect to G-Homa WiFi
- check the connection i.e. ping (default G-Homa AP IP: 10.10.100.254)
- run the configure command with params: python3 plug_configure.py plugip ctrlhost ctrlport ssid pskey

Example:

G-Homa Plug IP: 10.10.100.254

Your HA IP address: 192.168.1.10

Ghoma2mqtt port (use default 4196): 4196

WiFi name: Home-IoT

WiFi password: iot-home-gatdgets
```
python3 plug_configure.py 10.10.100.254 192.168.1.10 4196 Home-IoT iot-home-gatdgets
```

## Installation

Adding this add-ons repository to your Hass.io Home Assistant instance is
pretty easy. Follow https://home-assistant.io/hassio/installing_third_party_addons/ on the
website of Home Assistant, and use the following URL:

```
https://github.com/vneno/hassio-addons/
```

## Configuration

- MQTT_HOST - IP address of MQTT server (Leave empty to use internal mqtt)
- MQTT_PORT - 1883 (Leave empty to use internal mqtt)
- MQTT_SSL - if you want to use ssl (Leave empty when using internal mqtt)
- MQTT_USER - mqtt_username (Leave empty when using internal mqtt)
- MQTT_PASS - mqtt_password (Leave empty when using internal mqtt)
- RETAIN - retain MQTT messages
- AUTODISCOVERY - automatic device discovery in HA
- DISCOVERYTOPIC - default topic homeassistant
- DEBUG - debug messages in Log



### Thanks to:

https://github.com/poldy79/ghoma2mqtt

https://github.com/bl0x/ghomapy
