# CraftBeerPi

## Intro

CraftBeerPi is an open source brewing controller.

## Installation

CraftBeerPi is python based and will require at last python 3.7.x  
You can run CBPi 4.x on your Laptop. It's not required to use a Raspberry Pi.

Download an install Python 3.7  [https://www.python.org/downloads/](https://www.python.org/downloads/)

Open a terminal window and run the following commands.

```text
sudo python3 -m pip install cbpi
```

```text
cbpi setup
```

```text
cbpi start
```

The server is running under http://localhost:8000 by default.

### Installation from GitHub

You can install the latest master version direclty from GitHub.

```text
pip install https://github.com/Manuel83/craftbeerpi4/archive/master.zip
```

### Create a Python Virtual Environment

The advantage of a virtual enviroment is to separate the python dependencies.  
This is interesting for testing and to install several CBPi intances at the same time.

{% embed url="https://docs.python.org/3/library/venv.html" %}

```text
python3 -m venv venv

source venv/bin/activate
```

## Links

{% embed url="https://www.facebook.com/groups/craftbeerpi" %}

{% embed url="https://www.youtube.com/channel/UCy47sYaG8YLwJWw2iY5\_aNg" %}

{% embed url="http://web.craftbeerpi.com" %}

