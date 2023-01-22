#!/usr/bin/env bashio
set -e

CONFIG_PATH=/data/options.json


MQTT_HOST=$(bashio::config 'mqtt_host')
if [[ -z "$MQTT_HOST" || $MQTT_HOST == "null" ]]; then 
    if ! bashio::services.available "mqtt"; then
        bashio::log.error "No internal MQTT service found. Please install the internal Mosquitto MQTT broker integration."
    else
        bashio::log.info "Internal MQTT service found, fetching configuration ..."
        MQTT_HOST=$(bashio::services mqtt "host")
        MQTT_USER=$(bashio::services mqtt "username")
        MQTT_PASSWORD=$(bashio::services mqtt "password")

        RETAIN=$(jq --raw-output ".retain" $CONFIG_PATH)
        AUTODISCOVERY=$(jq --raw-output ".autodiscovery" $CONFIG_PATH)
        DISCOVERYTOPIC=$(jq --raw-output ".discoverytopic" $CONFIG_PATH)
        DEBUG=$(jq --raw-output ".debug" $CONFIG_PATH)

    fi
else
    # parse inputs from options
    MQTTHOST=$(jq --raw-output ".mqtt_host" $CONFIG_PATH)
    MQTTPORT=$(jq --raw-output ".mqtt_port" $CONFIG_PATH)
    MQTTSSL=$(jq --raw-output ".mqtt_ssl" $CONFIG_PATH)
    MQTTUSER=$(jq --raw-output ".mqtt_user" $CONFIG_PATH)
    MQTTPASS=$(jq --raw-output ".mqtt_pass" $CONFIG_PATH)
    RETAIN=$(jq --raw-output ".retain" $CONFIG_PATH)
    AUTODISCOVERY=$(jq --raw-output ".autodiscovery" $CONFIG_PATH)
    DISCOVERYTOPIC=$(jq --raw-output ".discoverytopic" $CONFIG_PATH)
    DEBUG=$(jq --raw-output ".debug" $CONFIG_PATH)

fi
bashio::log.info "Done."

bashio::log.info "Starting python script..."
python3 ghoma2mqtt_p3.py $MQTTHOST $MQTTPORT $MQTTSSL $MQTTUSER $MQTTPASS $RETAIN $AUTODISCOVERY $DISCOVERYTOPIC $DEBUG
bashio::log.info "Done."