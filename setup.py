from setuptools import setup, find_packages

setup(name='cbpi',
      version='4.0.3',
      description='CraftBeerPi API',
      author='Manuel Fritsch',
      author_email='manuel@craftbeerpi.com',
      url='http://web.craftbeerpi.com',
      packages=find_packages(),
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi': ['*','*.txt', '*.rst', '*.yaml']},

      install_requires=[
          "aiohttp==3.4.4",
          "aiohttp-auth==0.1.1",
          "aiohttp-route-decorator==0.1.4",
          "aiohttp-security==0.4.0",
          "aiohttp-session==2.7.0",
          "aiohttp-swagger==1.0.5",
          "aiojobs==0.2.2",
          "aiosqlite==0.7.0",
          "cryptography==2.3.1",
          "voluptuous==0.11.5",
          "pyfiglet==0.7.6"
      ],
        dependency_links=[
        'https://testpypi.python.org/pypi'
        ],
      entry_points = {
        "console_scripts": [
            "cbpi=cbpi.cli:main",
        ]
    }
)