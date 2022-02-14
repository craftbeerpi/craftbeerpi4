FROM alpine:latest as download
RUN apk --no-cache add curl && mkdir /downloads
# Download installation files
RUN curl https://github.com/avollkopf/craftbeerpi4-ui/archive/main.zip -L -o ./downloads/cbpi-ui.zip

FROM python:3.9 as base

# Install dependencies
RUN     apt-get update \
    &&  apt-get upgrade -y
RUN apt-get install --no-install-recommends -y \
    libatlas-base-dev \
    libffi-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv

# Create non-root user working directory
RUN groupadd -g 1000 -r craftbeerpi \
    && useradd -u 1000 -r -s /bin/false -g craftbeerpi craftbeerpi \
    && mkdir /cbpi \
    && chown craftbeerpi:craftbeerpi /cbpi \
    && mkdir -p $VIRTUAL_ENV \
    && chown -R craftbeerpi:craftbeerpi ${VIRTUAL_ENV}

USER craftbeerpi

# create virtual environment
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install craftbeerpi requirements for better caching
COPY --chown=craftbeerpi ./requirements.txt /cbpi-src/
RUN pip3 install --no-cache-dir -r /cbpi-src/requirements.txt

# Install RPi.GPIO separately because it's excluded in setup.py for non-raspberrys.
# This can enable GPIO support for the image when used on a raspberry pi and the
# /dev/gpiomem device.
RUN pip3 install --no-cache-dir RPi.GPIO==0.7.1

FROM base as deploy
# Install craftbeerpi from source
COPY --chown=craftbeerpi . /cbpi-src
RUN pip3 install --no-cache-dir /cbpi-src

# Install craftbeerpi-ui
COPY --from=download --chown=craftbeerpi /downloads /downloads
RUN pip3 install --no-cache-dir /downloads/cbpi-ui.zip

# Clean up installation files
USER root
RUN rm -rf /downloads /cbpi-src
USER craftbeerpi

WORKDIR /cbpi
RUN ["cbpi", "setup"]

EXPOSE 8000

# Start cbpi
CMD ["cbpi", "start"]
