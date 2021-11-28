# CraftBeerPi 4

[![Build](https://github.com/avollkopf/craftbeerpi4/actions/workflows/build.yml/badge.svg)](https://github.com/avollkopf/craftbeerpi4/actions/workflows/build.yml)
[![GitHub license](https://img.shields.io/github/license/avollkopf/craftbeerpi4)](https://github.com/avollkopf/craftbeerpi4/blob/master/LICENSE)
![GitHub issues](https://img.shields.io/github/issues-raw/Manuel83/craftbeerpi4)
![PyPI](https://img.shields.io/pypi/v/cbpi)
![Happy Brewing](https://img.shields.io/badge/CraftBeerPi%204-Happy%20Brewing-%23FBB117)

<p align="center">
  <img src="https://github.com/Manuel83/craftbeerpi4-ui/blob/main/cbpi4ui/public/logo192.png?raw=true" alt="CraftBeerPi Logo"/>
</p>

CraftBeerPi 4 is an open source software solution to control the brewing and
fermentation of beer :beer:.

## 📚 Documentation
Instructions on how to install CraftBeerPi and use its plugins is described
in the documentation, that can be found here: [gitbook.io](https://openbrewing.gitbook.io/craftbeerpi4_support/).

### Plugins
Plugins extend the base functionality of CraftBeerPi 4.
You can find a list of available plugins [here](https://openbrewing.gitbook.io/craftbeerpi4_support/master/plugin-installation#plugin-list).

### Docker image
While CraftbeerPi is primarily created to be run on a RaspberryPi
you can also use a docker image to run it. This let's you try CraftBeerPi
quickly without much installation overhead. It can also be very handy
when developing your own plugins.

Images are currently available for `arm64` and `amd64` architectures.
That means, that they won't run on a RaspberryPi unless you installed
a 64bit version of the OS. This is only a requirement for the docker image,
not if you install CraftBeerPi on the pi directly.

### Start a container
You can also use the image in your real setup with docker or docker-compose (or other orchestrators).

```bash
# setup the configuration directory for later use in a volume mount (must be done once)
mkdir config && chown :1000 config
docker run --rm -v "$(pwd)/config:/cbpi/config" ghcr.io/avollkopf/craftbeerpi4:latest cbpi setup

# run craftbeerpi
docker run -d -v "$(pwd)/config:/cbpi/config" -p 8000:8000 ghcr.io/avollkopf/craftbeerpi4:latest
```

or as compose file
```yml
version: "3.7"
services:
  craftbeerpi:
    image: ghcr.io/avollkopf/craftbeerpi4:latest
      volumes:
        - "./config:/cbpi/config"
      ports:
        - 8000:8000
```

Please note that this setup does not include GPIO functionality for CraftBeerPi 4.
You may be lucky with one of the methods described here to get it to work:
https://stackoverflow.com/questions/30059784/docker-access-to-raspberry-pi-gpio-pins

#### Install plugins in the container
You can create your own image based on `ghcr.io/avollkopf/craftbeerpi4` and install
plugins as `RUN` commands in the docker file as you would in a regular environment.

Sample `Dockerfile`
```Dockerfile
FROM ghcr.io/avollkopf/craftbeerpi4:vXX.XX.XX.XX

# Switch to root user for installing plugins
USER root

# Install plugins
RUN pip3 install --no-cache-dir cbpi4-pt100x

# Don't forget to switch back to craftbeerpi user
USER craftbeerpi

# Add plugin to craftbeerpi
RUN cbpi add cbpi4-pt100x
```
Then build the image
```bash
docker build . -t yourimagename
```
Then build and use your image in the `docker run` command or `docker-compose` file.

## 🧑‍🤝‍🧑 Contributers
Thanks to all the people who have contributed

[![contributors](https://contributors-img.web.app/image?repo=avollkopf/craftbeerpi4)](https://github.com/avollkopf/craftbeerpi4/graphs/contributors)
