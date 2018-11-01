import importlib

from aiohttp import web
from aiohttp_auth import auth
from core.cbpi import CraftBeerPi

cbpi = CraftBeerPi()




cbpi.start()