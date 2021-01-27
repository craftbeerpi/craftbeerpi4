# CraftBeerPi

## Intro

CraftBeerPi is an open source brewing controller.

![](.gitbook/assets/bildschirmaufnahme-2021-01-24-um-11.47.30.mov)

## Installation

CraftBeerPi is python based and will require at last python 3.7.x  
You can run CBPi 4.x on your Laptop. It's not required to use a Raspberry Pi.

Download an install Python 3.7  [https://www.python.org/downloads/](https://www.python.org/downloads/)

Open a terminal window and run the following commands.

#### Downloas the software via Python pip

```text
sudo python3 -m pip install cbpi
```

#### Setup Environment

```bash
cbpi setup
```

The setup command will create a config folder in directory where you executed this command. The config folder contains all instance data. For example all your hardware configuration and log files.

{% hint style="info" %}
You can setup as many enviroments as you like on one computer / Raspberry pi.  
Just navigate to a diffent folder and run the setup command again. This will create additional config folder
{% endhint %}

#### Run the Server

```text
cbpi start
```

The server is running under http://localhost:8000 by default.

#### Access the User Interface

```text
http://<YOUR_IP>:8000/
```

{% hint style="info" %}
Port 8000 is the default port. You can change this port in the config folder config.yaml
{% endhint %}

### Installation from GitHub

You can install the latest development version direclty from GitHub.

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

## Uninstall

```text
pip uninstall cbpi
```

## Links

{% embed url="https://www.facebook.com/groups/craftbeerpi" %}

{% embed url="https://www.youtube.com/channel/UCy47sYaG8YLwJWw2iY5\_aNg" %}

{% embed url="http://web.craftbeerpi.com" %}

