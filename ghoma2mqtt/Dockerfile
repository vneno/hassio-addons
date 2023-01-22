ARG BUILD_FROM
FROM $BUILD_FROM
#FROM python:3.6

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apt update && apt install -y jq
RUN pip3 --no-cache-dir install paho-mqtt

# Copy data for add-on
COPY ghoma2mqtt_p3.py /
COPY run.sh /

RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
#ENTRYPOINT [ "/run.sh" ]
#CMD [ "python3", "ghoma2mqtt_p3.py" ]
