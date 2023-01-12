#!/bin/bash
set -e

CONFIG_PATH=/data/options.json

# parse inputs from options
MQTTHOST=$(jq --raw-output ".MQTTHOST" $CONFIG_PATH)
MQTTPORT=$(jq --raw-output ".MQTTPORT" $CONFIG_PATH)
MQTTSSL=$(jq --raw-output ".MQTTSSL" $CONFIG_PATH)
MQTTUSER=$(jq --raw-output ".MQTTUSER" $CONFIG_PATH)
MQTTPASS=$(jq --raw-output ".MQTTPASS" $CONFIG_PATH)
RETAIN=$(jq --raw-output ".RETAIN" $CONFIG_PATH)
AUTODISCOVERY=$(jq --raw-output ".AUTODISCOVERY" $CONFIG_PATH)
DISCOVERYTOPIC=$(jq --raw-output ".DISCOVERYTOPIC" $CONFIG_PATH)
DEBUG=$(jq --raw-output ".DEBUG" $CONFIG_PATH)

echo "---"
echo "starting ghoma2mqtt"
python3 ghoma2mqtt_p3.py $MQTTHOST $MQTTPORT $MQTTSSL $MQTTUSER $MQTTPASS $RETAIN $AUTODISCOVERY $DISCOVERYTOPIC $DEBUG
