ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install craftbeerpi requirements for better caching
COPY ./requirements.txt /workspace/requirements.txt
RUN pip3 install --no-cache-dir -r /workspace/requirements.txt

# Install current version of cbpi-ui
RUN mkdir /opt/downloads \
    && curl https://github.com/avollkopf/craftbeerpi4-ui/archive/main.zip -L -o /opt/downloads/cbpi-ui.zip \
    && pip3 install --no-cache-dir /opt/downloads/cbpi-ui.zip \
    && rm -rf /opt/downloads