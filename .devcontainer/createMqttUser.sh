#!/bin/bash

USER=craftbeerpi
PASSWORD=craftbeerpi
docker run -it --rm -v "$(pwd)/mosquitto/config/mosquitto.passwd:/opt/passwdfile" eclipse-mosquitto:2 mosquitto_passwd -b /opt/passwdfile $USER $PASSWORD