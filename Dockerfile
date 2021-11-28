FROM alpine:latest as download
RUN apk --no-cache add curl && mkdir /downloads
# Download installation files
RUN curl https://github.com/avollkopf/craftbeerpi4-ui/archive/main.zip -L -o ./downloads/cbpi-ui.zip

FROM python:3.7

# Install dependencies
RUN     apt-get update \
    &&  apt-get upgrade -y
RUN apt-get install --no-install-recommends -y \
    libatlas-base-dev \
    libffi-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

WORKDIR /cbpi
# Create non-root user working directory
RUN groupadd -g 1000 -r craftbeerpi \
    && useradd -u 1000 -r -s /bin/false -g craftbeerpi craftbeerpi \
    && chown craftbeerpi:craftbeerpi /cbpi

# Install craftbeerpi from source
COPY . /cbpi-src
RUN pip3 install --no-cache-dir /cbpi-src

# Install craftbeerpi-ui
COPY --from=download /downloads /downloads
RUN pip3 install --no-cache-dir /downloads/cbpi-ui.zip

# Clean up installation files
RUN rm -rf /downloads /cbpi-src

USER craftbeerpi

RUN cbpi setup

EXPOSE 8000

# Start cbpi
CMD ["cbpi", "start"]