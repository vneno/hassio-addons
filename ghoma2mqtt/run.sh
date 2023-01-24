#!/usr/bin/env bashio
set -e

MQTT_HOST=$(bashio::config 'mqtt_host')
if [[ -z "$MQTT_HOST" || $MQTT_HOST == "null" ]]; then 
    if ! bashio::services.available "mqtt"; then
        bashio::log.error "No internal MQTT service found. Please install the internal Mosquitto MQTT broker integration."
    else
        bashio::log.info "Internal MQTT service found, fetching configuration ..."
        MQTT_HOST=$(bashio::services mqtt "host")
        MQTT_USER=$(bashio::services mqtt "username")
        MQTT_PASS=$(bashio::services mqtt "password")
	MQTT_PORT="1883"
        MQTT_SSL="NOSSL"

	RETAIN=$(bashio::config 'retain')
	AUTODISCOVERY=$(bashio::config 'autodiscovery')
        DISCOVERYTOPIC=$(bashio::config 'discoverytopic')
        DEBUG=$(bashio::config 'debug')


    fi
else
    # parse inputs from options
    MQTT_HOST=$(bashio::config 'mqtt_host')
    MQTT_PORT=$(bashio::config 'mqtt_port')
    MQTT_SSL=$(bashio::config 'mqtt_ssl')
    MQTT_USER=$(bashio::config 'mqtt_user')
    MQTT_PASS=$(bashio::config 'mqtt_pass')

    RETAIN=$(bashio::config 'retain')
    AUTODISCOVERY=$(bashio::config 'autodiscovery')
    DISCOVERYTOPIC=$(bashio::config 'discoverytopic')
    DEBUG=$(bashio::config 'debug')


fi
bashio::log.info "Done."

bashio::log.info "Starting python script..."
python3 ghoma2mqtt_p3.py $MQTT_HOST $MQTT_PORT $MQTT_SSL $MQTT_USER $MQTT_PASS $RETAIN $AUTODISCOVERY $DISCOVERYTOPIC $DEBUG
bashio::log.info "Done."
