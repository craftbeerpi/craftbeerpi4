FROM mcr.microsoft.com/vscode/devcontainers/python:3.9-bullseye

RUN     apt-get update \
    &&  apt-get upgrade -y
RUN apt-get install --no-install-recommends -y \
    libatlas-base-dev \
    libffi-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install craftbeerpi requirements and additional-dev-requirements for better caching
COPY ./requirements.txt ./.devcontainer/cbpi-default-dev-config/additional-dev-requirements.txt /workspace/
RUN cat /workspace/additional-dev-requirements.txt 2>/dev/null 1>> /workspace/requirements.txt \
    && pip3 install --no-cache-dir -r /workspace/requirements.txt

# Install current version of cbpi-ui
RUN mkdir /opt/downloads \
    && curl https://github.com/avollkopf/craftbeerpi4-ui/archive/main.zip -L -o /opt/downloads/cbpi-ui.zip \
    && pip3 install --no-cache-dir /opt/downloads/cbpi-ui.zip \
    && rm -rf /opt/downloads