from setuptools import setup, find_packages
from cbpi import __version__
import platform

# read the contents of your README file
from os import popen, path

localsystem = platform.system()
raspberrypi=False
if localsystem == "Linux":
    command="cat /proc/cpuinfo | grep Raspberry"
    model=popen(command).read()
    if len(model) != 0:
        raspberrypi=True

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cbpi4',
      version=__version__,
      description='CraftBeerPi4 Brewing Software',
      author='Manuel Fritsch / Alexander Vollkopf',
      author_email='manuel@craftbeerpi.com',
      url='http://web.craftbeerpi.com',
      license='GPLv3',
      project_urls={
	    'Documentation': 'https://openbrewing.gitbook.io/craftbeerpi4_support/'},
      packages=find_packages(),
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi': ['*','*.txt', '*.rst', '*.yaml']},

      python_requires='>=3.9',
      long_description=long_description,
	    long_description_content_type='text/markdown',
      install_requires=[
          "typing-extensions>=4",
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
