from aiohttp import web
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from blog_rest_api.config import CONFIG
from blog_rest_api.controllers import AuthController
from blog_rest_api.models import (User, Permission)
from blog_rest_api.utils import Struct


async def initialise_mongo(db):
    print('Initialising mongo ...')
    await User.q(db).create_indexes()
    await Permission.q(db).create_indexes()
    print('... mongo initialised.')


async def initialse(app):
    await initialise_mongo(app['db'])


def start():

    loop = asyncio.get_event_loop()
    client = AsyncIOMotorClient(io_loop=loop)

    app = web.Application()

    app['db'] = client.blog
    app['config'] = Struct(CONFIG)

    app.on_startup.append(initialse)

    auth_controller = AuthController()
    auth_controller.bind_routes(app)

    web.run_app(app)


if __name__ == "__main__":
    start()
