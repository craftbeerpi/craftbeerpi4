from setuptools import setup, find_packages
from cbpi import __version__
import platform

# read the contents of your README file
from os import popen

localsystem = platform.system()
raspberrypi=False
if localsystem == "Linux":
    command="cat /proc/cpuinfo | grep Raspberry"
    model=popen(command).read()
    if len(model) != 0:
        raspberrypi=True


setup(name='cbpi4',
      version=__version__,
      description='CraftBeerPi',
      author='Manuel Fritsch',
      author_email='manuel@craftbeerpi.com',
      url='http://web.craftbeerpi.com',
      packages=find_packages(),
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi': ['*','*.txt', '*.rst', '*.yaml']},

      python_requires='>=3.9',

      install_requires=[
          "aiohttp==3.8.1",
          "aiohttp-auth==0.1.1",
          "aiohttp-route-decorator==0.1.4",
          "aiohttp-security==0.4.0",
          "aiohttp-session==2.11.0",
          "aiohttp-swagger==1.0.16",
          "aiojobs==1.0.0 ",
          "aiosqlite==0.17.0",
          "cryptography==36.0.1",
          "requests==2.27.1",
          "voluptuous==0.12.2",
          "pyfiglet==0.8.post1",
          'click==8.0.4',
          'shortuuid==1.0.8',
          'tabulate==0.8.9',
          'asyncio-mqtt',
          'PyInquirer==1.0.3',
          'colorama==0.4.4',
          'psutil==5.9.0',
          'cbpi4gui',
          'importlib_metadata',
          'numpy==1.22.2',
          'pandas==1.4.1'] + (
          ['RPi.GPIO==0.7.1'] if raspberrypi else [] ),

        dependency_links=[
        'https://testpypi.python.org/pypi',
        
        ],
      entry_points = {
        "console_scripts": [
            "cbpi=cbpi.cli:main",
        ]
    }
)
