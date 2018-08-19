import logging
logger = logging.getLogger(__name__)

from aiohttp import web
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from blog_rest_api.config import CONFIG
from blog_rest_api.controllers import AuthController, UserController
from blog_rest_api.models import (User, Permission)
from blog_rest_api.utils import Struct

from blog_rest_api.initialisation import initialize, configure


def start():

    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    client = AsyncIOMotorClient(io_loop=loop)

    app = web.Application()

    app['db'] = client.blog
    app['config'] = Struct(CONFIG)

    app.on_startup.append(initialize)

    configure(app)

    web.run_app(app)


if __name__ == "__main__":
    start()
