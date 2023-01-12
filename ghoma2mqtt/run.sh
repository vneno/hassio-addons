#!/bin/bash
set -e

#CONFIG_PATH=/data/options.json
#CONNECTION_STRING="$(jq --raw-output '.connectionString' $CONFIG_PATH)"
#WATCH="$(jq --raw-output '.watch' $CONFIG_PATH)"

#echo Hello!
#node -v
#npm -v

echo "---"
echo "starting ghoma2mqtt"
python3 ghoma2mqtt_p3.py $MQTTHOST $MQTTPORT $MQTTSSL $MQTTUSER $MQTTPASS $RETAIN $AUTODISCOVERY $DISCOVERYTOPIC $DEBUG
