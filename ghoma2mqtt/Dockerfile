ARG BUILD_FROM
#FROM $BUILD_FROM
FROM python:3.6

ENV LANG C.UTF-8

# Copy data for add-on

COPY ghoma2mqtt_p3.py /

#RUN apt update && apt install -y vim

# Install requirements for add-on
#RUN apk add --no-cache npm
#RUN apk add --no-cache nodejs-npm 
#RUN apk add --no-cache nodejs-npm && npm install ghoma && npm install express && npm install multer && npm install body-parser
#RUN apk add --no-cache python-pip && pip -V
RUN pip3 --no-cache-dir install paho-mqtt
#RUN apk add --no-cache pip && pip install paho-mqtt
#RUN pip install paho-mqtt


# Python 3 HTTP Server serves the current working dir
# So let's set it to our add-on persistent data directory.
#WORKDIR /data


COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]
#ENTRYPOINT [ "/run.sh" ]
#CMD [ "python3", "ghoma2mqtt_p3.py" ]
