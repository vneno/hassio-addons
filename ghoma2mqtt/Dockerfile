ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --no-cache jq

# Hass.io CLI
ARG BUILD_ARCH
ARG CLI_VERSION
RUN pip3 install --no-cache-dir paho-mqtt

# Copy data for add-on
COPY ghoma2mqtt_p3.py /
COPY run.sh /

RUN chmod a+x /run.sh

ENTRYPOINT [ "/run.sh" ]
